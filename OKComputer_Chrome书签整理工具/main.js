// 全局变量
let bookmarkData = null;
let categorizedData = null;
let currentCategory = 'all';

// 分类规则定义
const categoryRules = {
    'work': {
        name: '工作学习',
        keywords: ['github', 'stackoverflow', 'gitlab', 'jira', 'confluence', 'notion', 'trello', 'slack', 'microsoft', 'google', 'docs', 'sheet', 'ppt'],
        domains: ['github.com', 'stackoverflow.com', 'gitlab.com', 'atlassian.net', 'notion.so', 'trello.com', 'slack.com', 'microsoft.com', 'google.com']
    },
    'social': {
        name: '社交媒体',
        keywords: ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok', 'weibo', 'wechat', 'qq', 'reddit', 'discord'],
        domains: ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com', 'tiktok.com', 'weibo.com', 'wechat.com', 'reddit.com', 'discord.com']
    },
    'shopping': {
        name: '购物消费',
        keywords: ['amazon', 'taobao', 'jd', 'tmall', 'alibaba', 'ebay', 'shopify', 'shopping', 'buy', 'store', 'mall'],
        domains: ['amazon.com', 'taobao.com', 'jd.com', 'tmall.com', 'alibaba.com', 'ebay.com', 'shopify.com']
    },
    'entertainment': {
        name: '娱乐休闲',
        keywords: ['netflix', 'spotify', 'steam', 'twitch', 'game', 'movie', 'music', 'video', 'anime', 'comic'],
        domains: ['netflix.com', 'spotify.com', 'steam.com', 'twitch.tv', 'youtube.com', 'bilibili.com']
    },
    'news': {
        name: '新闻资讯',
        keywords: ['news', 'bbc', 'cnn', 'reuters', 'techcrunch', 'medium', 'blog', 'article', 'journal', 'magazine'],
        domains: ['bbc.com', 'cnn.com', 'reuters.com', 'techcrunch.com', 'medium.com', 'wordpress.com']
    },
    'tools': {
        name: '工具软件',
        keywords: ['tool', 'app', 'software', 'download', 'online', 'converter', 'calculator', 'editor', 'viewer'],
        domains: ['online-convert.com', 'calculator.com', 'editor.com', 'viewer.com']
    },
    'education': {
        name: '教育学习',
        keywords: ['course', 'learn', 'study', 'education', 'university', 'school', 'academy', 'tutorial', 'lesson'],
        domains: ['coursera.org', 'edx.org', 'khanacademy.org', 'udemy.com', 'youtube.com']
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setupAnimations();
});

// 初始化应用
function initializeApp() {
    console.log('智能书签整理工具初始化...');
}

// 设置事件监听器
function setupEventListeners() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    // 拖拽上传
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);

    // 文件选择
    fileInput.addEventListener('change', handleFileSelect);

    // 点击上传区域
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });
}

// 设置动画
function setupAnimations() {
    // 页面加载动画
    anime({
        targets: '.fade-in',
        opacity: [0, 1],
        translateY: [30, 0],
        delay: anime.stagger(200),
        duration: 800,
        easing: 'easeOutQuart'
    });
}

// 拖拽处理函数
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

// 文件选择处理
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processFile(file);
    }
}

// 处理文件
function processFile(file) {
    if (!file.name.endsWith('.html') && !file.name.endsWith('.htm')) {
        showNotification('请选择HTML格式的书签文件', 'error');
        return;
    }

    showProgress(true);
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const htmlContent = e.target.result;
        parseBookmarks(htmlContent, file.name);
    };
    reader.readAsText(file);
}

// 显示进度
function showProgress(show) {
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    if (show) {
        progressContainer.classList.remove('hidden');
        
        // 模拟进度
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            
            progressBar.style.width = progress + '%';
            
            if (progress < 30) {
                progressText.textContent = '正在解析书签文件...';
            } else if (progress < 60) {
                progressText.textContent = '正在智能分类...';
            } else if (progress < 90) {
                progressText.textContent = '正在生成统计信息...';
            } else {
                progressText.textContent = '处理完成！';
            }
        }, 100);
    } else {
        progressContainer.classList.add('hidden');
    }
}

// 解析书签文件
function parseBookmarks(htmlContent, filename) {
    try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');
        
        // 提取书签数据
        const bookmarks = [];
        const links = doc.querySelectorAll('a');
        
        links.forEach((link, index) => {
            const bookmark = {
                id: index + 1,
                title: link.textContent.trim(),
                url: link.href,
                addDate: link.getAttribute('add_date') || Date.now(),
                icon: link.getAttribute('icon') || '',
                folder: getBookmarkFolder(link) || '未分类'
            };
            bookmarks.push(bookmark);
        });

        bookmarkData = {
            filename: filename,
            totalBookmarks: bookmarks.length,
            bookmarks: bookmarks,
            parseDate: new Date().toISOString()
        };

        // 智能分类
        setTimeout(() => {
            categorizedData = categorizeBookmarks(bookmarks);
            showResults();
        }, 1500);

    } catch (error) {
        console.error('解析书签文件时出错:', error);
        showNotification('文件解析失败，请检查文件格式', 'error');
        showProgress(false);
    }
}

// 获取书签所在文件夹
function getBookmarkFolder(link) {
    let parent = link.parentElement;
    while (parent) {
        if (parent.tagName === 'DL' && parent.previousElementSibling && parent.previousElementSibling.tagName === 'H3') {
            return parent.previousElementSibling.textContent.trim();
        }
        parent = parent.parentElement;
    }
    return null;
}

// 智能分类书签
function categorizeBookmarks(bookmarks) {
    const categories = {};
    const uncategorized = [];

    // 初始化分类
    Object.keys(categoryRules).forEach(key => {
        categories[key] = {
            name: categoryRules[key].name,
            bookmarks: [],
            color: getCategoryColor(key)
        };
    });

    // 分类每个书签
    bookmarks.forEach(bookmark => {
        const category = classifyBookmark(bookmark);
        if (category && categories[category]) {
            categories[category].bookmarks.push(bookmark);
        } else {
            uncategorized.push(bookmark);
        }
    });

    // 添加未分类书签
    if (uncategorized.length > 0) {
        categories['uncategorized'] = {
            name: '其他',
            bookmarks: uncategorized,
            color: '#6b7280'
        };
    }

    return categories;
}

// 分类单个书签
function classifyBookmark(bookmark) {
    const url = bookmark.url.toLowerCase();
    const title = bookmark.title.toLowerCase();
    
    for (const [categoryKey, rule] of Object.entries(categoryRules)) {
        // 检查域名匹配
        if (rule.domains) {
            for (const domain of rule.domains) {
                if (url.includes(domain)) {
                    return categoryKey;
                }
            }
        }
        
        // 检查关键词匹配
        if (rule.keywords) {
            for (const keyword of rule.keywords) {
                if (url.includes(keyword) || title.includes(keyword)) {
                    return categoryKey;
                }
            }
        }
    }
    
    return null;
}

// 获取分类颜色
function getCategoryColor(category) {
    const colors = {
        'work': '#3b82f6',
        'social': '#10b981',
        'shopping': '#f59e0b',
        'entertainment': '#ef4444',
        'news': '#8b5cf6',
        'tools': '#06b6d4',
        'education': '#84cc16',
        'uncategorized': '#6b7280'
    };
    return colors[category] || '#6b7280';
}

// 显示结果
function showResults() {
    showProgress(false);
    
    // 更新统计信息
    updateStatistics();
    
    // 显示分类结果
    showCategorizedResults();
    
    // 显示预览区域
    document.getElementById('preview-section').classList.remove('hidden');
    
    // 滚动到预览区域
    document.getElementById('preview-section').scrollIntoView({ 
        behavior: 'smooth' 
    });

    // 动画效果
    anime({
        targets: '#preview-section',
        opacity: [0, 1],
        translateY: [50, 0],
        duration: 800,
        easing: 'easeOutQuart'
    });
}

// 更新统计信息
function updateStatistics() {
    const statsContainer = document.getElementById('stats-container');
    const totalBookmarks = document.getElementById('total-bookmarks');
    const totalFolders = document.getElementById('total-folders');
    const processingTime = document.getElementById('processing-time');

    // 显示统计容器
    statsContainer.classList.remove('hidden');
    
    // 动画更新数字
    animateNumber(totalBookmarks, bookmarkData.totalBookmarks);
    animateNumber(totalFolders, Object.keys(categorizedData).length);
    animateNumber(processingTime, 2.3, 's');

    // 统计容器动画
    anime({
        targets: statsContainer.children,
        scale: [0.8, 1],
        opacity: [0, 1],
        delay: anime.stagger(200),
        duration: 600,
        easing: 'easeOutBack'
    });
}

// 数字动画
function animateNumber(element, target, suffix = '') {
    const obj = { value: 0 };
    anime({
        targets: obj,
        value: target,
        duration: 1000,
        easing: 'easeOutQuart',
        update: function() {
            element.textContent = Math.round(obj.value * 10) / 10 + suffix;
        }
    });
}

// 显示分类结果
function showCategorizedResults() {
    const categoryTabs = document.getElementById('category-tabs');
    const categoryContent = document.getElementById('category-content');

    // 生成分类标签
    categoryTabs.innerHTML = '';
    Object.entries(categorizedData).forEach(([key, category], index) => {
        const tab = document.createElement('button');
        tab.className = `category-tab px-4 py-2 rounded-lg font-medium transition-all ${index === 0 ? 'active' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`;
        tab.textContent = `${category.name} (${category.bookmarks.length})`;
        tab.onclick = () => switchCategory(key);
        categoryTabs.appendChild(tab);
    });

    // 显示第一个分类的内容
    switchCategory(Object.keys(categorizedData)[0]);
}

// 切换分类
function switchCategory(categoryKey) {
    currentCategory = categoryKey;
    const category = categorizedData[categoryKey];
    const categoryContent = document.getElementById('category-content');

    // 更新标签状态
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.classList.remove('active');
        tab.classList.add('bg-gray-200', 'text-gray-700');
    });
    event.target.classList.add('active');
    event.target.classList.remove('bg-gray-200', 'text-gray-700');

    // 生成书签卡片
    categoryContent.innerHTML = '';
    category.bookmarks.slice(0, 12).forEach((bookmark, index) => {
        const card = createBookmarkCard(bookmark, category.color);
        categoryContent.appendChild(card);
    });

    // 添加更多提示
    if (category.bookmarks.length > 12) {
        const moreCard = document.createElement('div');
        moreCard.className = 'bookmark-card bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl p-6 flex items-center justify-center text-center';
        moreCard.innerHTML = `
            <div>
                <div class="text-2xl font-bold text-gray-600 mb-2">+${category.bookmarks.length - 12}</div>
                <div class="text-gray-500">更多书签</div>
            </div>
        `;
        categoryContent.appendChild(moreCard);
    }

    // 动画效果
    anime({
        targets: '.bookmark-card',
        scale: [0.8, 1],
        opacity: [0, 1],
        delay: anime.stagger(100),
        duration: 400,
        easing: 'easeOutBack'
    });
}

// 创建书签卡片
function createBookmarkCard(bookmark, color) {
    const card = document.createElement('div');
    card.className = 'bookmark-card bg-white rounded-xl p-6 shadow-sm border border-gray-100';
    
    const favicon = getFaviconUrl(bookmark.url);
    const domain = new URL(bookmark.url).hostname;
    
    card.innerHTML = `
        <div class="flex items-start space-x-3">
            <img src="${favicon}" alt="" class="w-8 h-8 rounded" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xNiA5QzEyLjY4NjMgOSAxMCAxMS42ODYzIDEwIDE1QzEwIDE4LjMxMzcgMTIuNjg2MyAyMSAxNiAyMUMxOS4zMTM3IDIxIDIyIDE4LjMxMzcgMjIgMTVDMjIgMTEuNjg2MyAxOS4zMTM3IDkgMTYgOVpNMTYgMTlDMTMuNzkwOSAxOSAxMiAxNy4yMDkxIDEyIDE1QzEyIDEyLjc5MDkgMTMuNzkwOSAxMSAxNiAxMUMxOC4yMDkxIDExIDIwIDEyLjc5MDkgMjAgMTVDMjAgMTcuMjA5MSAxOC4yMDkxIDE5IDE2IDE5WiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K'">
            <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-gray-900 truncate mb-1" title="${bookmark.title}">${bookmark.title}</h3>
                <p class="text-sm text-gray-500 truncate mb-2">${domain}</p>
                <div class="flex items-center space-x-2">
                    <span class="inline-block w-2 h-2 rounded-full" style="background-color: ${color}"></span>
                    <span class="text-xs text-gray-400">${bookmark.folder}</span>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// 获取网站图标
function getFaviconUrl(url) {
    try {
        const domain = new URL(url).hostname;
        return `https://www.google.com/s2/favicons?domain=${domain}&sz=64`;
    } catch (error) {
        return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xNiA5QzEyLjY4NjMgOSAxMCAxMS42ODYzIDEwIDE1QzEwIDE4LjMxMzcgMTIuNjg2MyAyMSAxNiAyMUMxOS4zMTM3IDIxIDIyIDE4LjMxMzcgMjIgMTVDMjIgMTEuNjg2MyAxOS4zMTM3IDkgMTYgOVpNMTYgMTlDMTMuNzkwOSAxOSAxMiAxNy4yMDkxIDEyIDE1QzEyIDEyLjc5MDkgMTMuNzkwOSAxMSAxNiAxMUMxOC4yMDkxIDExIDIwIDEyLjc5MDkgMjAgMTVDMjAgMTcuMjA5MSAxOC4yMDkxIDE5IDE2IDE5WiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K';
    }
}

// 加载示例数据
function loadSampleData() {
    const sampleBookmarks = [
        { id: 1, title: 'GitHub', url: 'https://github.com', folder: '开发工具' },
        { id: 2, title: 'Stack Overflow', url: 'https://stackoverflow.com', folder: '开发工具' },
        { id: 3, title: 'YouTube', url: 'https://youtube.com', folder: '娱乐' },
        { id: 4, title: 'Netflix', url: 'https://netflix.com', folder: '娱乐' },
        { id: 5, title: 'Amazon', url: 'https://amazon.com', folder: '购物' },
        { id: 6, title: '淘宝', url: 'https://taobao.com', folder: '购物' },
        { id: 7, title: 'Facebook', url: 'https://facebook.com', folder: '社交' },
        { id: 8, title: 'Twitter', url: 'https://twitter.com', folder: '社交' },
        { id: 9, title: 'BBC News', url: 'https://bbc.com/news', folder: '新闻' },
        { id: 10, title: 'Coursera', url: 'https://coursera.org', folder: '学习' },
        { id: 11, title: 'Notion', url: 'https://notion.so', folder: '工具' },
        { id: 12, title: 'Slack', url: 'https://slack.com', folder: '工作' }
    ];

    bookmarkData = {
        filename: '示例书签.html',
        totalBookmarks: sampleBookmarks.length,
        bookmarks: sampleBookmarks,
        parseDate: new Date().toISOString()
    };

    categorizedData = categorizeBookmarks(sampleBookmarks);
    showResults();
    showNotification('示例数据加载完成！', 'success');
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white font-medium transform translate-x-full transition-transform duration-300`;
    
    switch (type) {
        case 'success':
            notification.classList.add('bg-green-500');
            break;
        case 'error':
            notification.classList.add('bg-red-500');
            break;
        case 'warning':
            notification.classList.add('bg-yellow-500');
            break;
        default:
            notification.classList.add('bg-blue-500');
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 导出功能（在results.html中实现更完整的导出功能）
function exportBookmarks(format) {
    if (!categorizedData) {
        showNotification('没有可导出的数据', 'warning');
        return;
    }

    switch (format) {
        case 'html':
            exportToHTML();
            break;
        case 'json':
            exportToJSON();
            break;
        case 'csv':
            exportToCSV();
            break;
        default:
            showNotification('不支持的导出格式', 'error');
    }
}

// 导出为HTML
function exportToHTML() {
    const html = generateBookmarkHTML(categorizedData);
    downloadFile(html, 'organized-bookmarks.html', 'text/html');
}

// 导出为JSON
function exportToJSON() {
    const json = JSON.stringify(categorizedData, null, 2);
    downloadFile(json, 'bookmarks-data.json', 'application/json');
}

// 导出为CSV
function exportToCSV() {
    const csv = generateBookmarkCSV(categorizedData);
    downloadFile(csv, 'bookmarks-data.csv', 'text/csv');
}

// 生成书签HTML
function generateBookmarkHTML(data) {
    let html = `<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>\n`;

    Object.entries(data).forEach(([key, category]) => {
        html += `<DT><H3>${category.name}</H3>\n<DL><p>\n`;
        
        category.bookmarks.forEach(bookmark => {
            const date = Math.floor(Date.now() / 1000);
            html += `<DT><A HREF="${bookmark.url}" ADD_DATE="${date}">${bookmark.title}</A>\n`;
        });
        
        html += `</DL><p>\n`;
    });

    html += `</DL><p>`;
    return html;
}

// 生成书签CSV
function generateBookmarkCSV(data) {
    let csv = 'Category,Title,URL,Folder\n';
    
    Object.entries(data).forEach(([key, category]) => {
        category.bookmarks.forEach(bookmark => {
            csv += `"${category.name}","${bookmark.title}","${bookmark.url}","${bookmark.folder}"\n`;
        });
    });
    
    return csv;
}

// 下载文件
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification(`文件已下载: ${filename}`, 'success');
}