"""
README - Thu tu chay Pipeline Phat hien Dao van
=================================================

TONG QUAN:
  Du lieu tho 300GB PDF arXiv -> pipeline xu ly -> app realtime phat hien dao van

THU TU CHAY:

  BUOC 1: Cau hinh moi truong
    File:     00_setup.sh
    Moi truong: Cloud Shell
    Thoi gian:  5 phut

  BUOC 2: Boc text tu PDF
    File:     01_extract_text.py
    Moi truong: Colab hoac VM (Python thuan, co checkpoint)
    Thoi gian:  3-5 gio (300GB, 16 threads)

  BUOC 3: Lam sach text (10 tang)
    File:     02_clean_text.py
    Moi truong: Colab hoac VM (Python thuan, co checkpoint)
    Thoi gian:  2-3 gio

  BUOC 4: Tao Silver+
    File:     03_silver_plus.py
    Moi truong: Dataproc Cluster (PySpark)
    Lenh:     gcloud dataproc jobs submit pyspark gs://BUCKET/scripts/03_silver_plus.py ...
    Thoi gian:  20-40 phut

  BUOC 5a: MinHash LSH Candidates (offline analysis)
    File:     04a_minhash_lsh.py
    Moi truong: Dataproc Cluster
    Lenh:     gcloud dataproc jobs submit pyspark gs://BUCKET/scripts/04a_minhash_lsh.py ...
    Thoi gian:  30-60 phut
    Muc dich:  Phan tich toan bo corpus, tim cap dao van -> bao cao

  BUOC 5b: Tao MinHash Signatures (song song)
    File:     04b_minhash_signatures.py
    Moi truong: Dataproc Cluster
    Lenh:     gcloud dataproc jobs submit pyspark gs://BUCKET/scripts/04b_minhash_signatures.py ...
    Thoi gian:  10-20 phut

  BUOC 5c: Build LSH Queryable Index
    File:     04c_build_lsh_index.py
    Moi truong: Master node cluster (SSH vao)
    Lenh:     python3 /tmp/04c_build_lsh_index.py
    Thoi gian:  5-15 phut
    Luu y:    PHAI chay SAU buoc 5b

  BUOC 5d: Export Chunks
    File:     04e_chunk_export.py
    Moi truong: Dataproc Cluster
    Thoi gian:  10-20 phut
    Luu y:    Co the chay SONG SONG voi buoc 5a, 5b

  BUOC 5e: Build FAISS Index
    File:     04d_build_faiss_index.py
    Moi truong: Colab (GPU) hoac VM co GPU
    Thoi gian:  1-2 gio (abstract only)
    Luu y:    PHAI chay SAU buoc 5d

  BUOC 6: Demo / Kiem tra
    File:     05_demo_check_pdf.py
    Moi truong: Colab (GPU)
    Thoi gian:  Load 2-3 phut, moi query 15-25 giay

CAU TRUC GCS SAU KHI CHAY XONG:

  gs://BUCKET/
    bronze/
      raw_pdfs/arxiv/          <- PDF goc
      raw_metadata/arxiv/      <- Metadata JSONL
    silver/
      arxiv_text_parquet/      <- Buoc 2: text tho
      arxiv_cleaned_parquet/   <- Buoc 3: text da clean
      arxiv_silver_plus/       <- Buoc 4: du lieu hoan chinh
    intermediate/
      lsh_candidates/          <- Buoc 5a: cap dao van offline
      minhash_signatures/      <- Buoc 5b: signatures
      minhash_index/           <- Buoc 5c: LSH queryable index
      chunks_parquet/          <- Buoc 5d: chunks
      faiss_index/             <- Buoc 5e: FAISS index
    gold/                      <- Ket qua cuoi cung

DEPENDENCY GRAPH:

  01 -> 02 -> 03 -> 04a (offline, cho bao cao)
                  -> 04b -> 04c (cho app realtime)
                  -> 04e -> 04d (cho app realtime)
                  
  04c + 04d -> 05 (demo)

LUU Y QUAN TRONG:
  - Tat cluster khi khong dung: gcloud dataproc clusters delete ...
  - 300GB can cluster 6+ workers (n2-standard-8)
  - FAISS chi embed abstract cho toc do, them introduction neu can
  - App realtime can Colab GPU (T4)
"""
