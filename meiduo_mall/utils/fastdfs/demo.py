from fdfs_client.client import Fdfs_client

if __name__ == '__main__':
    client = Fdfs_client('client.conf')

    # # 上传
    # data = client.upload_by_file('/home/python/Desktop/meizi.png')
    # print(data)
    """
    {
        'Remote file_id': 'group1/M00/00/02/rBEAAV2m5ZOATGdnABXyXx0Xf1g611.png',
         'Group name': 'group1',
         'Status': 'Upload successed.',
         'Storage IP': '172.17.0.1',
         'Uploaded size': '1.00MB',
         'Local file name': '/home/python/Desktop/meizi.png'
     }
    """

    # 修改====>内部实现有错误
    # data = client.modify_by_file('/home/python/Desktop/2.jpg', 'group1/M00/00/02/wKgvgV2mcQyAf2jIAAAhg8MeEWU331.jpg')
    # print(data)

    # 删除
    # data = client.delete_file('group1/M00/00/02/rBEAAV2m6o-AMLtHABXyXx0Xf1g408.png')
    # print(data)
    '''
    ('Delete file successed.', 'group1/M00/00/02/rBEAAV2m6o-AMLtHABXyXx0Xf1g408.png', '172.17.0.1')
    '''