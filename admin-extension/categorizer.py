#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书签分类引擎（动态多层嵌套 + 优先级可配）

设计：
- 4 种策略：folder_path / domain / keyword / ai
- 每个策略可独立启用/禁用、调整 priority
- 嵌套层数 max_depth 可配（默认 2）
- 分类路径用 / 分隔（如 "技术/前端/React"）

使用：
    categorizer = BookmarkCategorizer()
    category = categorizer.categorize(bookmark)  # "技术/前端"
"""

import json
import re
import logging
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger('api.categorizer')


# ============================================================================
# 策略基类
# ============================================================================


class Strategy:
    """分类策略基类"""

    def __init__(self, config: Dict):
        self.config = config
        self.weight = config.get('weight', 0.5)

    def match(self, bookmark: Dict) -> Optional[str]:
        """匹配分类路径，None 表示不匹配"""
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


# ============================================================================
# 具体策略
# ============================================================================


class FolderPathStrategy(Strategy):
    """策略 1：浏览器文件夹结构（最高优先级，0）"""

    def match(self, bookmark: Dict) -> Optional[str]:
        if not self.config.get('trust_browser_folders', False):
            return None

        folder_path = bookmark.get('folder_path', '').strip()
        if not folder_path:
            return None

        # 提取路径段（去掉 "Bookmarks Bar" 等根目录）
        parts = [
            p.strip() for p in folder_path.split('/')
            if p.strip() and p.strip() not in ('Bookmarks Bar', 'Other Bookmarks', 'Mobile Bookmarks', '')
        ]

        if not parts:
            return None

        return '/'.join(parts)


class DomainStrategy(Strategy):
    """策略 2：域名精确匹配（priority 1）"""

    def match(self, bookmark: Dict) -> Optional[str]:
        url = bookmark.get('url', '').strip()
        if not url:
            return None

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
        except Exception:
            return None

        mappings = self.config.get('mappings', {})

        # 精确匹配
        if domain in mappings:
            return mappings[domain]

        # 模糊匹配（子域名也匹配）
        for mapped_domain, category in mappings.items():
            if domain.endswith('.' + mapped_domain) or domain == mapped_domain:
                return category

        return None


class KeywordStrategy(Strategy):
    """策略 3：关键字匹配（priority 2）"""

    def match(self, bookmark: Dict) -> Optional[str]:
        text_parts = [
            bookmark.get('title', ''),
            bookmark.get('url', ''),
            bookmark.get('description', ''),
        ]
        text = ' '.join(text_parts).lower()

        if not text.strip():
            return None

        rules = self.config.get('rules', {})

        # 收集所有匹配的分类（支持多层级路径直接匹配）
        direct_matches = []    # 已含 / 的（如 "前端/React"）
        category_matches = []  # 单层（如 "前端"）

        for category, keywords in rules.items():
            if any(kw.lower() in text for kw in keywords):
                if '/' in category:
                    direct_matches.append(category)
                else:
                    category_matches.append(category)

        # 优先用直接多层级匹配
        if direct_matches:
            return direct_matches[0]

        # 否则用单层拼接（按配置顺序）
        if category_matches:
            return '/'.join(category_matches)

        return None


class AIStrategy(Strategy):
    """策略 4：AI 推荐（priority 3，最低优先）"""

    def match(self, bookmark: Dict) -> Optional[str]:
        api_base = self.config.get('api_endpoint', '/v1/ai/suggest')
        timeout = self.config.get('timeout', 10)

        try:
            # 调用已有 AI 推荐
            resp = requests.post(
                api_base,
                json={
                    "url": bookmark.get('url', ''),
                    "title": bookmark.get('title', ''),
                    "type": "category",
                },
                timeout=timeout,
            )
            if resp.ok:
                data = resp.json()
                category = data.get('category', '') or data.get('data', {}).get('category', '')
                if category:
                    return category
        except Exception as e:
            logger.debug(f"AI category failed: {e}")

        return self.config.get('fallback', '未分类')


# ============================================================================
# 引擎
# ============================================================================


class BookmarkCategorizer:
    """书签分类引擎：4 策略 + 优先级链 + 深度限制"""

    STRATEGY_REGISTRY = {
        'folder_path': FolderPathStrategy,
        'domain': DomainStrategy,
        'keyword': KeywordStrategy,
        'ai': AIStrategy,
    }

    def __init__(self, config_path: str = "config/categorization.json"):
        self.config = self._load_config(config_path)
        self.max_depth = self.config.get('max_depth', 2)
        self.separator = self.config.get('separator', '/')
        self.default_category = self.config.get('default_category', '未分类')
        self.strategies: List[Strategy] = []
        self._build_strategy_chain()

    def _load_config(self, path: str) -> Dict:
        """加载配置（支持环境变量覆盖）"""
        config_path = Path(path)
        if config_path.exists():
            with config_path.open('r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            logger.warning(f"Config not found: {path}, using default")
            config = self._default_config()

        # 支持环境变量覆盖
        import os
        if 'CATEGORY_MAX_DEPTH' in os.environ:
            config['max_depth'] = int(os.environ['CATEGORY_MAX_DEPTH'])
        if 'CATEGORY_STRATEGY_PRIORITY' in os.environ:
            # 格式："folder_path:0,domain:1,keyword:2,ai:3"
            for item in os.environ['CATEGORY_STRATEGY_PRIORITY'].split(','):
                name, prio = item.split(':')
                if name in config['strategies']:
                    config['strategies'][name]['priority'] = int(prio)

        return config

    def _default_config(self) -> Dict:
        return {
            "max_depth": 2,
            "separator": "/",
            "default_category": "未分类",
            "strategies": {
                "folder_path": {"enabled": True, "priority": 0},
                "domain": {"enabled": True, "priority": 1},
                "keyword": {"enabled": True, "priority": 2},
                "ai": {"enabled": True, "priority": 3},
            },
            "rules": {
                "domain": {"mappings": {}},
                "keyword": {"rules": {}},
            },
        }

    def _build_strategy_chain(self):
        """按 priority 升序构建策略链"""
        sorted_strategies = sorted(
            [(k, v) for k, v in self.config.get('strategies', {}).items()
             if v.get('enabled', False)],
            key=lambda x: x[1].get('priority', 99),
        )

        self.strategies = []
        for name, conf in sorted_strategies:
            strategy_cls = self.STRATEGY_REGISTRY.get(name)
            if not strategy_cls:
                logger.warning(f"Unknown strategy: {name}")
                continue
            rule_conf = self.config.get('rules', {}).get(name, conf)
            self.strategies.append(strategy_cls(rule_conf))

        logger.info(
            f"Categorizer built with {len(self.strategies)} strategies "
            f"(order: {[s.name for s in self.strategies]}, max_depth={self.max_depth})"
        )

    def categorize(self, bookmark: Dict) -> str:
        """对单个书签分类

        Returns:
            分类路径，如 "技术/前端" 或 fallback "未分类"
        """
        for strategy in self.strategies:
            try:
                result = strategy.match(bookmark)
                if result and self._validate_depth(result):
                    return result
            except Exception as e:
                logger.error(f"Strategy {strategy.name} failed: {e}")
                continue

        return self.default_category

    def categorize_batch(self, bookmarks: List[Dict]) -> List[Dict]:
        """批量分类

        Returns:
            [{"bookmark": {...}, "category": "...", "strategy": "..."}, ...]
        """
        results = []
        for bm in bookmarks:
            category = self.categorize(bm)
            # 找匹配的策略
            matched_strategy = "fallback"
            for strategy in self.strategies:
                try:
                    r = strategy.match(bm)
                    if r and self._validate_depth(r):
                        matched_strategy = strategy.name
                        break
                except Exception:
                    continue

            results.append({
                "bookmark": bm,
                "category": category,
                "strategy": matched_strategy,
            })

        return results

    def _validate_depth(self, path: str) -> bool:
        """验证路径深度不超过 max_depth"""
        if not path:
            return False
        depth = len(path.split(self.separator))
        return depth <= self.max_depth

    def update_max_depth(self, new_depth: int) -> None:
        """动态修改 max_depth（不重启）"""
        if 1 <= new_depth <= 5:
            self.max_depth = new_depth
            self.config['max_depth'] = new_depth
            logger.info(f"max_depth updated to {new_depth}")
        else:
            raise ValueError(f"max_depth must be 1-5, got {new_depth}")

    def get_config(self) -> Dict:
        """获取当前配置（脱敏）"""
        return {
            "max_depth": self.max_depth,
            "separator": self.separator,
            "default_category": self.default_category,
            "strategies_order": [
                {"name": s.name, "weight": s.weight}
                for s in self.strategies
            ],
            "domain_count": len(self.config.get('rules', {}).get('domain', {}).get('mappings', {})),
            "keyword_rules": list(self.config.get('rules', {}).get('keyword', {}).get('rules', {}).keys()),
        }


# ============================================================================
# 入口（供 admin 端调用）
# ============================================================================


_categorizer_singleton = None


def get_categorizer() -> BookmarkCategorizer:
    global _categorizer_singleton
    if _categorizer_singleton is None:
        _categorizer_singleton = BookmarkCategorizer()
    return _categorizer_singleton
