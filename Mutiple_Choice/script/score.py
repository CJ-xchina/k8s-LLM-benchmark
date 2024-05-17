import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calculate_accuracy(csv_file, jsonl_file, type='M'):
    # 读取 CSV 文件到 DataFrame
    df = pd.read_csv(csv_file)
    # 确保 'answer' 列存在
    if 'answer' not in df.columns:
        raise ValueError("CSV file must contain an 'answer' column")
    # 读取 JSONL 文件到 DataFrame
    jsonl_df = pd.read_json(jsonl_file, lines=True)

    # 确保 CSV 文件中的 'id' 列与 JSONL 文件中的 'id' 列可以对应起来
    df = df.merge(jsonl_df[['id', 'category', 'subcategory', 'score']], on='id', how='left')

    scores = df['score'].values
    # Exclude records where 'score' is less than 3
    # df = df[df['score'] >= 3]

    # 计算每个模型的准确率，并按 category 和 subcategory 分类
    model_scores = {}

    if type == 'O':
        # 处理包含 "_score" 的列
        score_columns = [col for col in df.columns if '_score' in col]

        for model in score_columns:
            if model == 'Mistral-7B-instruct-v2-lora':
                continue
            # 初始化得分统计字典
            model_scores[model] = {
                'overall': [],
                'category': {},
                'subcategory': {}
            }

            # 遍历每一行处理得分
            for index, row in df.iterrows():
                scores = row[model]
                if pd.notna(scores):
                    # 移除字符串中的 'nan' 并计算平均值
                    filtered_scores = [s for s in scores.split(',') if s.strip().lower() != 'nan']
                    if filtered_scores:
                        scores_list = list(map(float, filtered_scores))
                        avg_score = np.mean(scores_list)
                        model_scores[model]['overall'].append(avg_score)

                        # 分类统计
                        category = row['category']
                        subcategory = row['subcategory']

                        if category not in model_scores[model]['category']:
                            model_scores[model]['category'][category] = []
                        if subcategory not in model_scores[model]['subcategory']:
                            model_scores[model]['subcategory'][(category, subcategory)] = []

                        model_scores[model]['category'][category].append(avg_score)
                        model_scores[model]['subcategory'][(category, subcategory)].append(avg_score)

            # 计算平均得分
            for key in ['overall', 'category', 'subcategory']:
                if key == 'overall':
                    model_scores[model][key] = np.mean(model_scores[model][key]) if model_scores[model][key] else 0
                else:
                    for subkey in model_scores[model][key]:
                        model_scores[model][key][subkey] = np.mean(model_scores[model][key][subkey]) if \
                            model_scores[model][key][subkey] else 0

    elif type == 'M':
        for model in df.columns[2:-3]:  # 假设前两列是 'id' 和 'answer'，导数三列分别是'category','subcategory','socre'

            if model == 'Mistral-7B-instruct-v2-lora':
                continue

            # 初始化模型准确率字典
            model_scores[model] = {
                'overall': ((df['answer'] == df[model]).mean()) * 100,
                'category': {},
                'subcategory': {}
            }

            # 计算每个 category 和 subcategory 的准确率
            for category, category_df in df.groupby('category'):
                correct_predictions = (category_df['answer'] == category_df[model]).sum()
                total_predictions = category_df.shape[0]
                if total_predictions > 0:
                    cat_acc = correct_predictions / total_predictions * 100
                    model_scores[model]['category'][category] = cat_acc
                else:
                    model_scores[model]['category'][category] = 0

                for subcategory, subcategory_df in category_df.groupby('subcategory'):
                    # 计算当前 category 和 subcategory 下的准确率
                    correct_predictions = (subcategory_df['answer'] == subcategory_df[model]).sum()
                    total_predictions = subcategory_df.shape[0]
                    if total_predictions > 0:
                        cat_acc = correct_predictions / total_predictions * 100
                        model_scores[model]['subcategory'][(category, subcategory)] = cat_acc
                    else:
                        model_scores[model]['subcategory'][(category, subcategory)] = 0
            pass

    return model_scores, scores


def plot_score_distribution(scores):
    plt.figure(figsize=(8, 6))
    plt.hist(scores, bins=np.arange(min(scores), max(scores) + 1.5) - 0.5, color='skyblue', edgecolor='black',
             alpha=0.7)
    plt.title('Score Distribution')
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()


def plot_bar_chart(accuracy, save_path):
    def plot_subcategory_accuracy(accuracy):
        # Extract models
        models = list(accuracy.keys())

        # Determine all categories and their subcategories
        category_subcategories = {}
        for model, data in accuracy.items():
            for (cat_subcat, _) in data['subcategory'].items():
                cat, subcat = cat_subcat
                if cat not in category_subcategories:
                    category_subcategories[cat] = set()
                category_subcategories[cat].add(subcat)

        # Sort for consistent plotting
        for cat in category_subcategories:
            category_subcategories[cat] = sorted(category_subcategories[cat])

        # Plotting
        for category, subcategories in category_subcategories.items():
            fig, ax = plt.subplots(figsize=(12, 6))
            n_subcategories = len(subcategories)
            bar_width = 0.15
            index = np.arange(n_subcategories)

            # 添加随机猜测水平的虚线
            plt.axhline(y=25, color='red', linestyle='--', label='Random Chance')

            for i, model in enumerate(models):
                subcat_acc = [accuracy[model]['subcategory'].get((category, subcat), 0) for subcat in subcategories]
                plt.bar(index + i * bar_width, subcat_acc, bar_width, label=model)

            plt.xlabel('Subcategories')
            plt.ylabel('Accuracy (%)')
            plt.title(f'Subcategory-wise Accuracy Comparison in {category}')
            plt.xticks(index + bar_width * (len(models) - 1) / 2, subcategories, rotation=45, ha='right',
                       fontsize=9)  # Adjusted here
            plt.ylim(0, 100)
            plt.legend()
            plt.tight_layout()

            plt.savefig(os.path.join(save_path, f'{category}_subcategory_accuracy.png'))
            plt.show()

    # Plotting
    def plot_accuracy(accuracy):
        # Plotting Overall Accuracy per Model as a separate plot
        overall_acc = {model: acc['overall'] for model, acc in accuracy.items()}
        plt.figure(figsize=(8, 6))
        plt.bar(overall_acc.keys(), overall_acc.values(), color='skyblue')
        plt.title('Overall Accuracy per Model')
        plt.xlabel('Model')
        plt.ylabel('Accuracy (%)')
        plt.ylim(0, 100)
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(os.path.join(save_path, 'overall_accuracy.png'))
        plt.show()
        plot_subcategory_accuracy(accuracy)

    def plot_category_accuracy(accuracy):
        # Extract models and categories
        models = list(accuracy.keys())
        categories = list(accuracy[models[0]]['category'].keys())

        # Sort categories for consistent plotting
        categories = sorted(categories)

        # Determine the number of categories, subcategories, and models
        n_categories = len(categories)
        n_models = len(models)

        # Plotting
        fig, ax = plt.subplots(figsize=(14, 8))

        # Define the width of the bars and the position of each bar
        bar_width = 0.25
        index = np.arange(n_categories)

        # Color map for the models
        cmap = plt.get_cmap('tab10')
        model_colors = [cmap(i) for i in range(len(models))]

        # Plot each subcategory for each model as a group of bars
        for i, model in enumerate(models):
            model_acc = [accuracy[model]['category'].get(category, 0) for category in categories]
            bar_plot = ax.bar(index + i * bar_width, model_acc, bar_width, label=model, color=model_colors[i])

            # Add the value labels on the bars
            for j, (bar, acc) in enumerate(zip(bar_plot, model_acc)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height, f'{acc:.3f}%',
                        ha='center', va='bottom')

        # Adding labels, title, and legend
        ax.set_xlabel('Category')
        ax.set_ylabel('Accuracy (%)')
        ax.set_title('Category-wise Accuracy Comparison Across Models')
        ax.set_xticks(index + bar_width * (n_models - 1) / 2)
        ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=10)

        # Adjust legend to display model names clearly
        legend = ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        # Set the y-axis limit to 0-100
        ax.set_ylim(0, 100)

        # Save the figure and show it
        plt.tight_layout()

        plt.savefig(os.path.join(save_path, 'category_wise_accuracy.png'))
        plt.show()

    plot_accuracy(accuracy)
    plot_category_accuracy(accuracy)


def plot_radar_chart(accuracy, save_path):
    def calculate_category_averages(accuracy):
        # 准备数据结构
        categories = list(accuracy[next(iter(accuracy))]['category'].keys())
        models = list(accuracy.keys())
        scores = {model: [] for model in models}

        for category in categories:
            for model in models:
                score = accuracy[model]['category'].get(category, 0)
                scores[model].append(score)

        # 添加每个模型所有类别的平均分
        for model in models:
            average_score = np.mean(scores[model])  # 计算平均分
            scores[model].append(average_score)  # 将平均分添加到分数列表的末尾

        # 更新类别列表以包括“平均”类别
        categories.append('Average')

        return scores, categories, models

    scores, categories, models = calculate_category_averages(accuracy)
    labels = np.array(categories)
    num_vars = len(labels)

    # 计算角度
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # 雷达图应该是闭合的，所以要将起始值复制到末尾
    scores = {model: np.concatenate((scores[model], [scores[model][0]])) for model in models}
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    for model in models:
        ax.fill(angles, scores[model], alpha=0.25, label=model)

    # 美化图表
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=13)

    # 添加图例位于图表下方
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

    # 保存图像
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'category_wise_accuracy_polar.png'))
    plt.show()


def plot_combined_accuracy(mcq_accuracy, essay_accuracy):
    models = list(mcq_accuracy.keys())
    categories = ['K8s Code Commands', 'K8s Knowledge Base', 'K8s Real-World Problems']

    fig, ax = plt.subplots(figsize=(10, 7))
    bar_height = 0.35
    y = np.arange(len(models))

    # Colors for differentiating MCQ and Essay for each category
    mcq_colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    essay_colors = ['#aec7e8', '#ffbb78', '#98df8a']

    for i, model in enumerate(models):

        mcq_scores = [mcq_accuracy[model]['category'].get(cat, 0) for cat in categories]
        essay_scores = [essay_accuracy[model + "_score"]['category'].get(cat, 0) for cat in categories]

        # Combined scores to create stacked bar segments
        bottom = np.zeros(len(models))
        for j, (mcq, essay) in enumerate(zip(mcq_scores, essay_scores)):
            ax.barh(y[i], mcq, bar_height, left=bottom[i], label=f'MCQ {categories[j]}' if i == 0 else "",
                    color=mcq_colors[j])
            bottom[i] += mcq
        for j, (mcq, essay) in enumerate(zip(mcq_scores, essay_scores)):
            ax.barh(y[i], essay, bar_height, left=bottom[i], label=f'Essay {categories[j]}' if i == 0 else "",
                    color=essay_colors[j])
            bottom[i] += essay

    # Adding labels, title, and custom y-axis tick labels, etc.
    ax.set_ylabel('Model')
    ax.set_yticks(y)
    ax.set_yticklabels(models)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')

    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Remove x-axis label
    ax.set_xlabel('Score ')

    plt.tight_layout()
    plt.show()


# 选择题部分

# 路径到 CSV 文件和 JSONL 文件
csv_file_M = "../resources/result.csv"
jsonl_file_M = "../resources/ops_data_en_improve.jsonl"
result_path_Mul = "../resources/result/Multiple"
accuracy_Mul, scores = calculate_accuracy(csv_file_M, jsonl_file_M)

# 问答题部分
csv_file_O = "../resources/result_obj.csv"
jsonl_file_O = "../resources/questions.json"
result_path_Obj = "../resources/result/Objective"
accuracy_obj, scores = calculate_accuracy(csv_file_O, jsonl_file_O, type='O')

# 计算准确率并绘制柱状图

#
# plot_bar_chart(accuracy_Mul, result_path_Mul)
#
# plot_radar_chart(accuracy_Mul, result_path_Mul)
#
# plot_bar_chart(accuracy_obj, result_path_Obj)
#
# plot_radar_chart(accuracy_obj, result_path_Obj)

plot_combined_accuracy(accuracy_Mul, accuracy_obj)
