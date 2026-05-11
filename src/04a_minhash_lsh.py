"""
04a_minhash_lsh.py - MinHash LSH Candidates 
Chay tren: Dataproc Cluster
Submit: gcloud dataproc jobs submit pyspark gs://BUCKET/scripts/04a_minhash_lsh.py \
            --cluster=bigdata-n9-ptit --region=asia-southeast1

PySpark ML hash + groupBy (KHONG dung approxSimilarityJoin)
Output: gs://BUCKET/intermediate/lsh_candidates/ (HIGH / MEDIUM)
"""

import re as re_module
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, BooleanType, ArrayType, StructType, StructField, DoubleType
from pyspark.ml.feature import CountVectorizer, NGram, RegexTokenizer, MinHashLSH
from pyspark.ml.linalg import SparseVector, DenseVector

BUCKET = "bigdata-n9-ptit-final"
INPUT = "gs://{}/silver/arxiv_silver_plus/".format(BUCKET)
OUTPUT = "gs://{}/intermediate/lsh_candidates/".format(BUCKET)

SHINGLE_K = 5
NUM_HASH_TABLES = 5
HIGH_THRESHOLD = 0.7
MEDIUM_THRESHOLD = 0.5

spark = SparkSession.builder \
    .appName("MinHash_LSH") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.memoryOverhead", "1g") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Doc + chuan bi text
print("[1/7] Doc du lieu...")
df = spark.read.parquet(INPUT)
df_text = df.select("paper_id", F.coalesce(
    F.concat_ws(" ", F.col("abstract"), F.col("introduction"), F.col("body")),
    F.col("clean_text")).alias("text")
).filter(F.col("text").isNotNull() & (F.length(F.col("text")) > 200))
print("  So bai: {}".format(df_text.count()))

# PySpark ML pipeline
print("[2/7] Tokenize + NGram + CountVectorizer...")
tokenizer = RegexTokenizer(inputCol="text", outputCol="words", pattern="\\W+", minTokenLength=2)
df_words = tokenizer.transform(df_text).filter(F.size("words") >= 20)
ngram = NGram(n=SHINGLE_K, inputCol="words", outputCol="shingles")
df_shingles = ngram.transform(df_words).filter(F.size("shingles") > 0)
cv = CountVectorizer(inputCol="shingles", outputCol="features", minDF=2.0, vocabSize=1 << 18)
cv_model = cv.fit(df_shingles)
df_features = cv_model.transform(df_shingles)

@F.udf(BooleanType())
def has_nonzero(v):
    if v is None: return False
    if isinstance(v, SparseVector): return len(v.indices) > 0
    return True

df_features = df_features.filter(has_nonzero("features"))
print("  So bai hop le: {}".format(df_features.count()))

# MinHash transform (khong dung approxSimilarityJoin)
print("[3/7] MinHash transform...")
mh = MinHashLSH(inputCol="features", outputCol="hashes", numHashTables=NUM_HASH_TABLES)
mh_model = mh.fit(df_features)
df_hashed = mh_model.transform(df_features).select("paper_id", "hashes").cache()
print("  Da hash: {}".format(df_hashed.count()))

# GroupBy band hash
print("[4/7] Tim candidates...")

@F.udf(StringType())
def extract_hash_val(band_idx, hash_vec):
    if hash_vec is None: return None
    return "b{}_{}".format(band_idx, int(hash_vec[0]))

df_bands = df_hashed.select("paper_id", F.posexplode("hashes").alias("band_idx", "hash_vec"))
df_bands = df_bands.withColumn("band_hash", extract_hash_val("band_idx", "hash_vec")).select("paper_id", "band_hash")

df_groups = df_bands.groupBy("band_hash").agg(F.collect_set("paper_id").alias("papers")) \
    .filter((F.size("papers") >= 2) & (F.size("papers") <= 100))

@F.udf(ArrayType(StructType([StructField("p1", StringType()), StructField("p2", StringType())])))
def make_pairs(papers):
    papers = sorted(papers)
    return [{"p1": papers[i], "p2": papers[j]} for i in range(len(papers)) for j in range(i+1, len(papers))]

df_pairs = df_groups.withColumn("pairs", make_pairs("papers"))
df_pairs = df_pairs.select(F.explode("pairs").alias("pair"))
df_pairs = df_pairs.select(F.col("pair.p1").alias("paper_a"), F.col("pair.p2").alias("paper_b")).distinct()
print("  Candidates: {}".format(df_pairs.count()))

# Tinh Jaccard tu hash agreement
print("[5/7] Tinh Jaccard...")
df_sim = df_pairs \
    .join(df_hashed.withColumnRenamed("paper_id","paper_a").withColumnRenamed("hashes","ha"), on="paper_a") \
    .join(df_hashed.withColumnRenamed("paper_id","paper_b").withColumnRenamed("hashes","hb"), on="paper_b")

@F.udf(DoubleType())
def hash_jaccard(ha, hb):
    if not ha or not hb: return 0.0
    return float(sum(1 for a, b in zip(ha, hb) if a[0] == b[0])) / len(ha)

df_sim = df_sim.withColumn("jaccard_similarity", hash_jaccard("ha", "hb"))
df_sim = df_sim.filter(F.col("jaccard_similarity") >= MEDIUM_THRESHOLD).select("paper_a", "paper_b", "jaccard_similarity")

# Loc cap cung arxiv ID
print("[6/7] Loc...")

@F.udf(StringType())
def base_id(pid):
    if not pid: return None
    return re_module.sub(r'v\d+$', '', pid.replace("arxiv_", "").replace(".pdf", ""))

df_sim = df_sim.withColumn("ba", base_id("paper_a")).withColumn("bb", base_id("paper_b"))
df_sim = df_sim.filter(F.col("ba") != F.col("bb")).drop("ba", "bb")
print("  Sau loc: {}".format(df_sim.count()))

# Phan loai + luu
print("[7/7] Luu...")
result = df_sim.withColumn("similarity_level",
    F.when(F.col("jaccard_similarity") >= HIGH_THRESHOLD, "HIGH").otherwise("MEDIUM")
).select("paper_a", "paper_b", "jaccard_similarity", "similarity_level")

result.groupBy("similarity_level").count().show()
result.write.partitionBy("similarity_level").mode("overwrite").parquet(OUTPUT)
result.filter(F.col("similarity_level") == "HIGH").orderBy(F.desc("jaccard_similarity")).show(10, truncate=False)

spark.stop()
print("Hoan thanh! -> {}".format(OUTPUT))
