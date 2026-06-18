# 数据清洗流程图

> 本文档使用 Mermaid 语法描述完整的数据清洗流程
> 可在支持 Mermaid 的编辑器（如 VS Code、Notion、GitHub）中渲染

---

## 1. 整体架构图

```mermaid
flowchart TB
    subgraph 前端层 ["前端层 (React + TypeScript)"]
        UI1["文件上传组件"]
        UI2["进度展示组件"]
        UI3["清洗报告页面"]
        UI4["用户操作界面"]
    end
    
    subgraph 接入层 ["接入层 (Flask API)"]
        API1["Upload API"]
        API2["WebSocket"]
        API3["Report API"]
        API4["Import API"]
    end
    
    subgraph 服务层 ["服务层 (Python)"]
        SVC1["清洗管道 orchestrator"]
        SVC2["解析服务 Parser"]
        SVC3["清洗服务 Cleaner"]
        SVC4["分析服务 Analyzer"]
        SVC5["验证服务 Validator"]
    end
    
    subgraph 存储层 ["存储层"]
        ST1["临时缓存 (Redis/File)"]
        ST2["书签数据 (JSON)"]
    end
    
    UI1 -->|"1. POST /upload"| API1
    API1 -->|"2. 启动任务"| SVC1
    SVC1 -->|"3. 分发任务"| SVC2
    SVC2 --> SVC3
    SVC3 --> SVC4
    SVC4 --> SVC5
    SVC1 <-->|"4. 实时进度"| API2
    API2 --> UI2
    SVC1 -->|"5. 缓存结果"| ST1
    UI3 -->|"6. GET /report"| API3
    API3 --> ST1
    UI4 -->|"7. POST /import"| API4
    API4 -->|"8. 持久化"| ST2
```

---

## 2. 前端详细流程

```mermaid
flowchart TD
    Start([用户点击"导入书签"]) --> CheckAuth{检查登录}
    CheckAuth -->|未登录| Login["跳转登录"]
    Login --> Start
    CheckAuth -->|已登录| UploadPage["步骤1: 上传页面"]
    
    UploadPage --> FileSelect["文件选择"]
    FileSelect --> FileValidate["文件验证"]
    
    FileValidate -->|格式错误| Error1["显示错误: 请上传HTML文件"]
    FileValidate -->|过大| Error2["显示错误: 文件超过10MB"]
    FileValidate -->|成功| Options["清洗选项配置"]
    
    Error1 --> FileSelect
    Error2 --> FileSelect
    
    Options --> Option1["☑️ 自动去重"]
    Options --> Option2["☑️ 检查失效链接"]
    Options --> Option3["☑️ 智能分类"]
    Options --> Option4["相似度阈值: 85%"]
    
    Option1 --> StartClean["开始清洗"]
    Option2 --> StartClean
    Option3 --> StartClean
    Option4 --> StartClean
    
    StartClean --> UploadAPI["POST /upload"]
    UploadAPI -->|"返回 task_id"| ProgressPage["步骤2: 处理进度页"]
    
    ProgressPage --> WSConnect["建立 WebSocket"]
    WSConnect --> ProgressBar["进度条展示"]
    ProgressBar --> Stage1["📄 解析中..."]
    Stage1 --> Stage2["🧹 清洗中..."]
    Stage2 --> Stage3["🔍 分析中..."]
    Stage3 --> Stage4["✅ 完成"
    ]
    
    Stage4 --> ReportPage["步骤3: 清洗报告页"]
    
    ReportPage --> Summary["统计概览"]
    Summary --> Card1["原始: 150条"]
    Summary --> Card2["清洗后: 138条"]
    Summary --> Card3["重复: 5组"]
    Summary --> Card4["建议: 45条"]
    
    ReportPage --> Tabs["Tab切换"]
    Tabs --> Tab1["⚠️ 重复项(3)"]
    Tabs --> Tab2["🔗 失效链接(2)"]
    Tabs --> Tab3["💡 优化建议(45)"]
    
    Tab1 --> DupGroup1["相似组1"]
    DupGroup1 --> DupAction1{"用户操作"}
    DupAction1 -->|合并| Merge1["保留选中项"]
    DupAction1 -->|保留全部| KeepAll1["不做处理"]
    DupAction1 -->|删除| Delete1["删除选中项"]
    
    Tab2 --> InvalidList["失效链接列表"]
    InvalidList --> InvalidAction{"批量操作"}
    InvalidAction -->|删除全部| DeleteAll
    InvalidAction -->|保留| KeepInvalid
    InvalidAction -->|逐个决定| DecideOne
    
    Tab3 --> SuggestionList["建议列表"]
    SuggestionList --> SuggestionItem["单项建议"]
    SuggestionItem --> SugAction{"操作"}
    SugAction -->|应用| ApplySug
    SugAction -->|忽略| IgnoreSug
    SugAction -->|编辑| EditSug["弹窗编辑"]
    
    Merge1 --> ConfirmImport
    KeepAll1 --> ConfirmImport
    Delete1 --> ConfirmImport
    DeleteAll --> ConfirmImport
    KeepInvalid --> ConfirmImport
    DecideOne --> ConfirmImport
    ApplySug --> ConfirmImport
    IgnoreSug --> ConfirmImport
    EditSug --> ConfirmImport
    
    ConfirmImport["确认导入"] --> ImportAPI["POST /import"]
    ImportAPI --> ResultPage["步骤4: 结果页"]
    
    ResultPage --> Success["导入成功 138条"]
    ResultPage --> Partial["部分成功 135/138"]
    ResultPage --> Fail["导入失败"]
    
    Partial --> Retry["重试失败项"]
    Retry --> ImportAPI
    
    Fail --> BackToReport["返回报告页"]
    BackToReport --> ConfirmImport
    
    Success --> ViewBookmarks["查看书签列表"]
    
    style Start fill:#e3f2fd
    style Success fill:#e8f5e9
    style Fail fill:#ffebee
```

---

## 3. 后端详细流程

```mermaid
flowchart TD
    Receive["接收上传请求"] --> SaveTemp["保存临时文件"]
    
    subgraph ParseStage ["阶段1: 解析"]
        SaveTemp --> ParseHTML["BeautifulSoup 解析 HTML"]
        ParseHTML --> ExtractDL["提取 DL/DT/A 标签"]
        ExtractDL --> BuildTree["构建文件夹树"]
        BuildTree --> ExtractMeta["提取元数据"]
        ExtractMeta --> RawData["原始书签数据"]
    end
    
    subgraph PreprocessStage ["阶段2: 预处理"]
        RawData --> NormalizeURL["URL 标准化"]
        NormalizeURL --> RemoveTrack["移除跟踪参数"]
        RemoveTrack --> CleanTitle["标题清洗"]
        CleanTitle --> ExtractDomain["提取域名"]
        ExtractDomain --> ParseTime["解析时间戳"]
    end
    
    subgraph CleanStage ["阶段3: 清洗"]
        ParseTime --> Deduplicate["精确去重"]
        Deduplicate --> CheckExact{"URL 相同?"}
        CheckExact -->|是| MarkDup["标记重复组"]
        CheckExact -->|否| KeepUnique
        MarkDup --> KeepLatest["保留最新添加"]
        
        KeepUnique --> StandardizeCat["分类标准化"]
        StandardizeCat --> CheckCat{"分类有效?"}
        CheckCat -->|否| MarkReclassify["标记待重分类"]
        CheckCat -->|是| PassCat
        MarkReclassify --> PassCat
        
        PassCat --> SimilarCheck["相似度检查"]
        SimilarCheck --> CalcSim["计算标题相似度"]
        CalcSim --> GroupSim["分组相似项"]
        GroupSim --> MarkSimilar["标记相似组"]
    end
    
    subgraph ValidateStage ["阶段4: 验证"]
        MarkSimilar --> CheckURL["URL 有效性检查"]
        CheckURL --> AsyncCheck["异步 HTTP 检查"]
        AsyncCheck --> CheckStatus{"状态码"}
        CheckStatus -->|2xx| MarkValid["标记有效"]
        CheckStatus -->|3xx| MarkRedirect["标记重定向"]
        CheckStatus -->|4xx/5xx| MarkInvalid["标记失效"]
        CheckStatus -->|超时| MarkTimeout["标记超时"]
    end
    
    subgraph AnalyzeStage ["阶段5: 分析"]
        MarkValid --> KeywordMatch["关键词匹配"]
        MarkRedirect --> KeywordMatch
        MarkTimeout --> KeywordMatch
        
        KeywordMatch --> SuggestCat["推荐分类"]
        SuggestCat --> SuggestTags["推荐标签"]
        SuggestTags --> GenAlias["生成别名"]
        GenAlias --> CalcConfidence["计算置信度"]
    end
    
    subgraph ReportStage ["阶段6: 生成报告"]
        CalcConfidence --> CompileStats["编译统计信息"]
        CompileStats --> BuildSummary["构建概览"]
        BuildSummary --> CacheResult["缓存结果"]
    end
    
    CacheResult --> WaitConfirm["等待用户确认"]
    
    subgraph ImportStage ["阶段7: 导入"]
        WaitConfirm --> ReceiveConfirm["接收导入请求"]
        ReceiveConfirm --> ApplyDecision["应用用户决策"]
        ApplyDecision --> MergeDup["合并重复项"]
        ApplyDecision --> DeleteInvalid["删除失效项"]
        ApplyDecision --> ApplySug["应用优化建议"]
        
        MergeDup --> CheckExist["检查已存在"]
        DeleteInvalid --> CheckExist
        ApplySug --> CheckExist
        
        CheckExist --> ExistAction{"已存在?"}
        ExistAction -->|是+更新| UpdateExist["更新书签"]
        ExistAction -->|是+跳过| SkipBookmark["跳过"]
        ExistAction -->|否| CreateNew["创建新书签"]
        
        UpdateExist --> SaveStorage
        SkipBookmark --> SaveStorage
        CreateNew --> SaveStorage["保存到存储"]
        
        SaveStorage --> CleanTemp["清理临时文件"]
    end
    
    CleanTemp --> ReturnResult["返回导入结果"]
    ReturnResult --> End([结束])
    
    style ParseStage fill:#e3f2fd
    style CleanStage fill:#fff3e0
    style AnalyzeStage fill:#f3e5f5
    style ImportStage fill:#e8f5e9
```

---

## 4. 数据流转图

```mermaid
flowchart LR
    subgraph Input ["输入数据"]
        HTML["bookmarks.html"]
    end
    
    subgraph Stage1 ["解析后"]
        RAW["原始数据 List[Dict]"]
        RAW_FIELDS["- title<br/>- url<br/>- add_date<br/>- folder_path"]
    end
    
    subgraph Stage2 ["预处理后"]
        NORM["标准化数据"]
        NORM_FIELDS["- title (清洗后)<br/>- url (标准化)<br/>- domain<br/>- added_date (ISO)"]
    end
    
    subgraph Stage3 ["清洗后"]
        CLEAN["清洗数据"]
        CLEAN_FIELDS["- 去重标记<br/>- 相似组 ID<br/>- 分类标准化<br/>- URL 状态"]
    end
    
    subgraph Stage4 ["分析后"]
        ANALYZED["分析数据"]
        ANALYZED_FIELDS["- suggested_category<br/>- suggested_tags<br/>- suggested_alias<br/>- confidence"]
    end
    
    subgraph Stage5 ["报告数据"]
        REPORT["清洗报告"]
        REPORT_FIELDS["- summary<br/>- exact_duplicates<br/>- similar_groups<br/>- invalid_urls<br/>- suggestions"]
    end
    
    subgraph Stage6 ["导入数据"]
        IMPORT["最终书签"]
        IMPORT_FIELDS["- title<br/>- url<br/>- tags<br/>- category<br/>- added_date"]
    end
    
    HTML -->|"parser.parse"| RAW
    RAW --> RAW_FIELDS
    RAW -->|"preprocess"| NORM
    NORM --> NORM_FIELDS
    NORM -->|"clean"| CLEAN
    CLEAN --> CLEAN_FIELDS
    CLEAN -->|"analyze"| ANALYZED
    ANALYZED --> ANALYZED_FIELDS
    ANALYZED -->|"generate_report"| REPORT
    REPORT --> REPORT_FIELDS
    REPORT -->|"apply_user_decisions"| IMPORT
    IMPORT --> IMPORT_FIELDS
```

---

## 5. WebSocket 实时进度流程

```mermaid
sequenceDiagram
    participant C as 客户端
    participant WS as WebSocket
    participant S as 清洗服务
    
    C->>WS: 连接 /ws/clean/:task_id
    WS-->>C: 连接成功
    
    loop 解析阶段
        S->>S: 每处理10条
        S->>WS: 推送进度
        WS->>C: {stage: "parsing", current: 50, total: 150}
        C->>C: 更新进度条
    end
    
    S->>WS: {stage: "cleaning", message: "正在去重..."}
    WS->>C: 更新阶段
    
    loop 清洗阶段
        S->>S: 发现重复组
        S->>WS: 推送详情
        WS->>C: {duplicates_found: 5}
    end
    
    S->>WS: {stage: "analyzing", message: "AI分析中..."}
    WS->>C: 更新阶段
    
    loop 分析阶段
        S->>S: 每分析10条
        S->>WS: 推送进度
        WS->>C: {current: 100, suggestions: 30}
    end
    
    alt 启用URL检查
        S->>WS: {stage: "validating", message: "检查链接有效性..."}
        WS->>C: 更新阶段
        
        loop URL检查
            S->>S: 每检查5条
            S->>WS: 推送进度
            WS->>C: {checked: 50, invalid: 2}
        end
    end
    
    S->>WS: {type: "complete", summary: {...}}
    WS->>C: 显示完成
    C->>WS: 关闭连接
```

---

## 6. 错误处理流程

```mermaid
flowchart TD
    subgraph UploadErrors ["上传阶段错误"]
        E1["文件格式错误"]
        E2["文件过大"]
        E3["文件损坏"]
    end
    
    subgraph ParseErrors ["解析阶段错误"]
        E4["HTML结构无效"]
        E5["编码错误"]
        E6["无书签数据"]
    end
    
    subgraph ProcessErrors ["处理阶段错误"]
        E7["内存不足"]
        E8["超时"]
        E9["分析失败"]
    end
    
    subgraph ImportErrors ["导入阶段错误"]
        E10["数据已过期"]
        E11["存储失败"]
        E12["部分失败"]
    end
    
    E1 --> Msg1["提示: 请上传Chrome/Firefox导出的HTML文件"]
    E2 --> Msg2["提示: 文件超过10MB限制，请分批导入"]
    E3 --> Msg3["提示: 文件损坏，请重新导出"]
    
    E4 --> Msg4["提示: HTML格式异常，尝试容错解析"]
    E5 --> Msg5["提示: 自动转换编码中..."]
    E6 --> Msg6["提示: 未检测到书签数据"]
    
    E7 --> Msg7["提示: 数据量过大，已切换为分批处理"]
    E8 --> Msg8["提示: 处理超时，可重试"]
    E9 --> Msg9["提示: 基础分析完成，AI分析跳过"]
    
    E10 --> Msg10["提示: 数据已过期，请重新上传"]
    E11 --> Msg11["提示: 存储失败，请检查权限"]
    E12 --> Msg12["提示: 部分导入成功，显示失败明细"]
    
    Msg4 --> Retry1["容错解析"]
    Msg5 --> Retry2["编码转换"]
    Msg8 --> Retry3["用户重试"]
    
    Msg12 --> ShowDetail["显示失败列表"]
    ShowDetail --> RetryImport["重试失败项"]
```

---

## 7. 状态机图

### 任务状态流转

```mermaid
stateDiagram-v2
    [*] --> PENDING: 创建任务
    
    PENDING --> PARSING: 开始解析
    PARSING --> PREPROCESSING: 解析完成
    PREPROCESSING --> CLEANING: 预处理完成
    
    CLEANING --> VALIDATING: 启用URL检查
    CLEANING --> ANALYZING: 跳过URL检查
    
    VALIDATING --> ANALYZING: 验证完成
    
    ANALYZING --> COMPLETED: 分析完成
    
    COMPLETED --> IMPORTING: 用户确认导入
    IMPORTING --> IMPORTED: 导入完成
    IMPORTING --> PARTIAL_IMPORTED: 部分失败
    
    PARTIAL_IMPORTED --> IMPORTING: 重试
    
    PENDING --> FAILED: 初始化失败
    PARSING --> FAILED: 解析失败
    CLEANING --> FAILED: 处理失败
    VALIDATING --> FAILED: 验证失败
    ANALYZING --> FAILED: 分析失败
    IMPORTING --> FAILED: 导入失败
    
    FAILED --> [*]
    IMPORTED --> [*]
    PARTIAL_IMPORTED --> [*]
    
    note right of COMPLETED
        等待用户操作
        15分钟后过期
    end note
```

---

## 8. 并发处理流程

```mermaid
flowchart TD
    subgraph ParallelProcessing ["并行处理设计"]
        Start["开始处理"]
        
        Start --> Split["数据分片<br/>每片50条"]
        
        Split --> P1["处理器1"]
        Split --> P2["处理器2"]
        Split --> P3["处理器3"]
        Split --> PN["处理器N..."]
        
        P1 --> R1["结果1"]
        P2 --> R2["结果2"]
        P3 --> R3["结果3"]
        PN --> RN["结果N"]
        
        R1 --> Merge["合并结果"]
        R2 --> Merge
        R3 --> Merge
        RN --> Merge
        
        Merge --> Final["最终结果"]
    end
    
    subgraph URLCheckConcurrency ["URL检查并发控制"]
        URLs["待检查URL列表"]
        Semaphore["信号量限制=10"]
        
        URLs --> Semaphore
        Semaphore --> C1["检查1"]
        Semaphore --> C2["检查2"]
        Semaphore --> C10["检查10"]
        
        C1 --> Done1["完成"]
        C2 --> Done2["完成"]
        C10 --> Done10["完成"]
        
        Done1 --> Semaphore
        Done2 --> Semaphore
        Done10 --> Semaphore
    end
```

---

*流程图使用 Mermaid 语法，可在支持 Mermaid 的编辑器中渲染查看*
