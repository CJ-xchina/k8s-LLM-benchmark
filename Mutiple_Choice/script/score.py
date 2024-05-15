import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calculate_accuracy_per_category_subcategory(csv_file, jsonl_file):
    # 读取 CSV 文件到 DataFrame
    df = pd.read_csv(csv_file)
    # 确保 'answer' 列存在
    if 'answer' not in df.columns:
        raise ValueError("CSV file must contain an 'answer' column")
    # 读取 JSONL 文件到 DataFrame
    jsonl_df = pd.read_json(jsonl_file, lines=True)

    # 确保 CSV 文件中的 'id' 列与 JSONL 文件中的 'id' 列可以对应起来
    df = df.merge(jsonl_df[['id', 'category', 'subcategory', 'score']], on='id', how='left')

    # Exclude records where 'score' is less than 3
    df = df[df['score'] >= 3]

    # 计算每个模型的准确率，并按 category 和 subcategory 分类
    model_acc = {}
    for model in df.columns[2:-3]:  # 假设前两列是 'id' 和 'answer'，导数三列分别是'category','subcategory','socre'
        # 初始化模型准确率字典
        model_acc[model] = {
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
                model_acc[model]['category'][category] = cat_acc
            else:
                model_acc[model]['category'][category] = 0

            for subcategory, subcategory_df in category_df.groupby('subcategory'):
                # 计算当前 category 和 subcategory 下的准确率
                correct_predictions = (subcategory_df['answer'] == subcategory_df[model]).sum()
                total_predictions = subcategory_df.shape[0]
                if total_predictions > 0:
                    cat_acc = correct_predictions / total_predictions * 100
                    model_acc[model]['subcategory'][(category, subcategory)] = cat_acc
                else:
                    model_acc[model]['subcategory'][(category, subcategory)] = 0
    return model_acc


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

        # 添加每隔10%的虚线
        # for i in range(30, 101, 10):  # 从30%到100%，每隔10%
        #     plt.axhline(y=i, color='gray', linestyle='--', linewidth=0.5)

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
        plt.savefig(f'../resources/result/{category}_subcategory_accuracy.png')
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
    plt.savefig('../resources/result/overall_accuracy.png')
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
    plt.savefig('../resources/result/category_wise_accuracy.png')
    plt.show()



# 选择题部分

# 路径到 CSV 文件和 JSONL 文件
csv_file = "../resources/result.csv"
jsonl_file = "../resources/ops_data_en_improve.jsonl"
# 计算准确率并绘制柱状图
accuracy = calculate_accuracy_per_category_subcategory(csv_file, jsonl_file)
plot_accuracy(accuracy)
# Now you can call this function after calculating the accuracy
plot_category_accuracy(accuracy)
# 问答题部分






