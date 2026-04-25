import mysql.connector
import sys

def test_connection(host):
    print(f"尝试连接到 {host}...")
    try:
        conn = mysql.connector.connect(
            host=host,
            user='root',
            password='root',
            database='job_result_db',
            port=3306,
            connect_timeout=5,
            consume_results=True,
            use_pure=True  # 尝试使用纯 Python 实现，排除 C 扩展问题
        )
        print(f"成功连接到 {host}!")
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        print(f"MySQL 版本: {cursor.fetchone()[0]}")
        conn.close()
    except Exception as e:
        print(f"连接 {host} 失败: {e}")

if __name__ == "__main__":
    test_connection("172.18.0.2")
    print("-" * 20)
    test_connection("localhost")
