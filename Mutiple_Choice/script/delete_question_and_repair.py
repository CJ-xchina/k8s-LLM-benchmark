import json

import pandas as pd


# 读取JSONL文件并转换为列表
def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]
    return data


# 读取CSV文件并转换为DataFrame
def read_csv(file_path):
    return pd.read_csv(file_path)


# 删除指定id的JSON对象和CSV行，并重新排列ID
def remove_and_renumber_entries(jsonl_data, csv_data, entry_ids_to_remove):
    # 从CSV中删除指定id的行
    csv_data = csv_data[~csv_data['id'].isin(entry_ids_to_remove)]

    # 从JSONL中删除指定id的对象，并获取剩余数据的ID列表
    remaining_ids = [entry['id'] for entry in jsonl_data if entry['id'] not in entry_ids_to_remove]

    # 旧、新 ID 映射
    id_map = {}
    # 重新排列ID，使其连续
    renumbered_jsonl_data = []
    new_id = 1
    for entry in jsonl_data:
        if entry['id'] not in entry_ids_to_remove:
            id_map[entry['id']] = new_id
            entry['id'] = new_id
            renumbered_jsonl_data.append(entry)
            new_id += 1

    # 将新的ID映射应用到CSV中
    csv_data.loc[:, 'id'] = csv_data['id'].map(id_map.get, na_action='ignore')
    return renumbered_jsonl_data, csv_data


# 将更新后的JSONL列表写回到新的JSONL文件
def write_jsonl(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for entry in data:
            file.write(json.dumps(entry) + '\n')


# 将更新后的CSV DataFrame写回到新的CSV文件
def write_csv(data, file_path):
    data.to_csv(file_path, index=False)


# 主函数
def main():
    # 假设文件路径如下
    jsonl_file = '../resources/ops_data_en_improve.jsonl'
    csv_file = '../resources/result.csv'

    # 读取数据
    jsonl_data = read_jsonl(jsonl_file)
    csv_data = read_csv(csv_file)

    # 用户输入要删除的id，使用空格分隔
    entry_ids_to_remove_input = input("请输入要删除的id，使用空格分隔: ")
    entry_ids_to_remove = set(map(int, entry_ids_to_remove_input.split()))

    # 删除操作
    updated_jsonl_data, updated_csv_data = remove_and_renumber_entries(jsonl_data, csv_data, entry_ids_to_remove)

    # 写入更新后的数据
    write_jsonl(updated_jsonl_data, jsonl_file)
    write_csv(updated_csv_data, csv_file)

    print("已删除指定的id条目，并更新了文件。")


if __name__ == "__main__":
    main()
