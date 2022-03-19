import os
 
def deleteFiles():
    for root, dirs, files in os.walk(wanted_del_file_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name in del_file_list:
                print("-" * 20)
                print('delete:%s' % file_path)  # 查看删除文件具体路径
                os.remove(file_path)
  
if __name__ == '__main__':
    wanted_del_file_dir = u'/home/abigail/Desktop/mysocket/client_computer'  # 要批量删除文件的最上级文件夹
    del_file_list = ['file.txt']
 
    deleteFiles()
    print('删除完成！')
