我将提供详细的手动测试步骤说明，你可以按照这些步骤自行测试混合房间路由Demo。

手动测试步骤指南
1. 环境准备
首先进入项目目录并安装依赖：

# 进入项目目录
cd D:\files\mempalace

# 安装BM25依赖（如果未安装）
pip install rank-bm25
2. 运行验证脚本（基础功能测试）
运行快速验证脚本来确认所有组件正常工作：

python demo_hybrid/verify_demo.py
预期输出：

============================================================
  Hybrid Room Routing Verification
============================================================

  Verifying all components...

[1] Testing BM25Retriever...
------------------------------------------------------------
  [OK] BM25 index created successfully
  [OK] Search returned 5 results
  [OK] Top result: Room 'database', Score 1.000

[2] Testing HybridRetriever...
------------------------------------------------------------
  [OK] Hybrid retriever created
  [OK] Fusion returned 10 results
  [OK] Top result: Fused=0.545, Dense=0.350, Sparse=1.000

[3] Testing RoomAggregator...
------------------------------------------------------------
  [OK] Aggregator created with method='average'
  [OK] Aggregation returned 2 rooms
  [OK] Top room: 'database', Score=0.825, Docs=2

[4] Testing Complete Pipeline...
------------------------------------------------------------
  [OK] Expected room 'database' found in top results

============================================================
  Verification Summary
============================================================
  BM25Retriever       : [OK] PASS
  HybridRetriever     : [OK] PASS
  RoomAggregator      : [OK] PASS
  Complete Pipeline   : [OK] PASS
3. 运行完整Demo（交互式测试）
运行主Demo程序，你可以选择不同模式进行测试：

python demo_hybrid/main.py
测试选项：

选项1：运行所有测试查询
程序会自动运行8个预定义的测试查询
显示每个查询的完整管道结果
验证混合搜索对不同查询类型的表现
选项2：运行单个查询Demo
测试默认查询 "database migration strategy"
显示详细的四阶段结果：
密集检索（模拟ChromaDB）
稀疏检索（BM25关键词匹配）
分数融合（α * dense + β * sparse）
房间聚合（按房间分组评分）
选项3：比较聚合方法
对同一查询比较不同的聚合方法：
average：房间内所有文档的平均分
max：房间内最高文档分数
weighted：根据排名加权的平均分
选项4：交互式模式
你可以输入自己的查询进行测试
尝试不同类型的查询：
关键词密集型：尝试 "JWT tokens"、"PostgreSQL migration"
语义密集型：尝试 "how do we handle authentication"
混合类型：尝试 "frontend component library documentation"
4. 运行评估套件（全面测试）
运行评估脚本进行系统性能测试：

python demo_hybrid/evaluate.py
评估内容：

检索精度比较：对比四种方法的房间级准确率
密集检索（语义相似度）
稀疏检索（BM25关键词）
混合检索（加权融合）
RRF（交替融合）
权重调优实验：测试不同α和β组合
(0.5, 0.5)、(0.7, 0.3)、(0.9, 0.1)等
聚合方法对比：比较三种聚合方法的效果
5. 手动验证核心组件
如果你想更深入地测试单个组件，可以直接在Python交互环境中测试：

# 启动Python交互环境
python

# 导入测试数据
>>> from demo_hybrid.test_data import TEST_DOCUMENTS, TEST_METADATAS
>>> print(f"测试数据：{len(TEST_DOCUMENTS)}个文档，分布在{len(set(m['room'] for m in TEST_METADATAS))}个房间")

# 测试BM25检索器
>>> from mempalace.sparse_retriever import BM25Retriever
>>> retriever = BM25Retriever(TEST_DOCUMENTS, TEST_METADATAS)
>>> results = retriever.search("database migration", k=5)
>>> print(f"BM25检索结果：{len(results)}个文档")

# 测试混合检索器
>>> from mempalace.hybrid_retriever import HybridRetriever
>>> # 创建模拟的密集检索结果
>>> dense_results = [(i, 0.3 + (i % 5) * 0.1) for i in range(len(TEST_DOCUMENTS))]
>>> hybrid = HybridRetriever(TEST_DOCUMENTS, TEST_METADATAS, alpha=0.7, beta=0.3)
>>> fused = hybrid.fuse_results(dense_results, results, k=10)
>>> print(f"融合结果：{len(fused)}个文档")

# 测试房间聚合器
>>> from mempalace.room_aggregator import RoomAggregator
>>> aggregator = RoomAggregator(method='average')
>>> room_results = aggregator.aggregate(fused, TEST_DOCUMENTS, TEST_METADATAS, top_k_rooms=3)
>>> print(f"房间结果：{len(room_results)}个房间")
6. 测试不同查询类型
你可以创建测试脚本来验证不同查询类型的表现：

# create_test.py
test_queries = [
    ("database backup strategy", "keyword_heavy"),
    ("authentication system design", "semantic_heavy"),
    ("JWT tokens with OAuth", "mixed"),
    ("React component library", "keyword_heavy"),
    ("improving application performance", "semantic_heavy"),
]

for query, query_type in test_queries:
    print(f"\n测试查询：{query} (类型：{query_type})")
    # 在这里运行混合搜索并打印结果
7. 验证数据完整性
检查测试数据是否正确：

from demo_hybrid.test_data import get_test_data
documents, metadatas, queries, stats = get_test_data()

print(f"文档数量：{stats['total_documents']}")
print(f"房间数量：{stats['total_rooms']}")
print("房间分布：")
for room, count in stats['rooms'].items():
    print(f"  {room}: {count}个文档")
8. 测试边界情况
测试边界情况确保鲁棒性：

空查询：测试空字符串查询
无结果查询：测试不相关的查询
单个房间查询：测试只有一个相关文档的情况
多房间查询：测试跨多个房间的复杂查询
9. 性能测试
测试系统性能：

import time

# 测试查询速度
start = time.time()
# 运行10次查询
for i in range(10):
    results = retriever.search("database", k=10)
end = time.time()
print(f"平均查询时间：{(end - start)/10:.3f}秒")
10. 预期测试结果
成功测试的标志：

✅ 验证脚本通过所有测试（4/4）
✅ 所有查询都能返回合理结果
✅ 混合检索比单一检索效果更好
✅ 房间聚合能正确分组相关文档
✅ 不同聚合方法产生合理差异
保存测试结果
你可以将测试结果保存到文件：

# 保存验证结果
```
python demo_hybrid/verify_demo.py > verification_results.txt
```
# 保存评估结果
```
python demo_hybrid/evaluate.py > evaluation_results.txt
```
# 保存单个查询演示
```
python -c "
from demo_hybrid.main import run_hybrid_search_demo
from demo_hybrid.test_data import TEST_DOCUMENTS, TEST_METADATAS
results = run_hybrid_search_demo('database migration', TEST_DOCUMENTS, TEST_METADATAS)
" > query_results.txt
```
快速启动命令
将这些命令保存为 test_commands.txt 文件：

# 1. 安装依赖
pip install rank-bm25

# 2. 验证所有组件
python demo_hybrid/verify_demo.py

# 3. 运行完整演示（选择选项1查看所有查询）
python demo_hybrid/main.py

# 4. 运行评估
python demo_hybrid/evaluate.py

# 5. 测试特定查询（例如：authentication）
python -c "
from demo_hybrid.main import run_hybrid_search_demo
from demo_hybrid.test_data import TEST_DOCUMENTS, TEST_METADATAS
run_hybrid_search_demo('authentication system', TEST_DOCUMENTS, TEST_METADATAS)
"
常见问题排查
如果测试失败，检查：

✅ BM25依赖是否正确安装
✅ 文件路径是否正确
✅ Python版本是否为3.9+
✅ 测试数据是否完整
所有测试都设计为完全自动化，你只需运行脚本即可验证完整的混合房间路由系统功能。