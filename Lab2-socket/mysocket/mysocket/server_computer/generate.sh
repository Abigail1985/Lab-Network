for i in {1..15}; do cat file.txt file.txt > file2.txt && mv file2.txt file.txt; done

# 生成 384kB
# buffer容量 1024*60*8B，480kB
