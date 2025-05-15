import os
import subprocess
from subprocess import TimeoutExpired

with open('urls.txt', 'r') as file:
    # for i in range(0, 129):
        # url = file.readline()
    for line in file:
        url = line.strip()  # 去除行尾的换行符
        try:
            # 添加20秒超时限制
            subprocess.run(
                f"npx dl-librescore@latest -i {url} -o ./downloads/ -t midi",
                shell=True,
                check=True,
                timeout=20
            )
        except TimeoutExpired:
            print(f"跳过 {url} (超时)")
        except Exception as e:
            print(f"错误 {url}: {str(e)}")