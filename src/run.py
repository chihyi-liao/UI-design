# 載入二進位專案並啟動
try:
    from project.__main__ import main

    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"找不到或無法載入核心動態庫: {e}")
