from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # To avoid multithreading issues with matplotlib as it doesnot support multithreading so we have to use it 
import matplotlib.pyplot as plt
from io import BytesIO
from scipy.stats import skew
import base64

app = Flask(__name__, static_folder='static')


df = pd.read_csv("sales.csv")

@app.route('/')
def home():
    categories = df['category'].unique()
    return render_template('index.html', categories=categories)

def assess_item_status(category, item,max_sales_month):
    try:
        filtered_data = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == max_sales_month)]
        print(f"Filtered Data for {category} - {item} - {max_sales_month}:\n{filtered_data}")

        total_quantity_sold = filtered_data['quantity_sold'].sum()

        threshold_quantity = 1000  # You can adjust this threshold based on your data and criteria

        item_status = "Asset" if total_quantity_sold >= threshold_quantity else "Liability"
        return f"{item} in {category} is classified as: {item_status} (Total Quantity Sold: {total_quantity_sold})"
        
    except Exception as e:
        print(f"Error in assess_item_status: {e}")
        return f""
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/get_items', methods=['POST'])
def get_items():
    category = request.form['category']
    items = df[df['category'] == category]['item'].unique().tolist()
    return jsonify({'items': items})

def create_plot(category, item, month, chart_type):
    try:
        filtered_data = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)]

        if chart_type == 'bar':
            plot_data = filtered_data.groupby('brand').agg({'quantity_sold': 'sum', 'price': 'sum'}).reset_index()
            x = plot_data['brand']
            y1 = plot_data['quantity_sold']
            y2 = plot_data['price']
            title = f'Sales for {item} in {category} - {month}'
            ylabel = 'Quantity Sold'
        elif chart_type == 'pie':
            plot_data = filtered_data.groupby('brand')['quantity_sold'].sum().reset_index()
            labels = plot_data['brand']
            sizes = plot_data['quantity_sold']
            title = f'Share of Sales for {item} in {category} - {month}'
        else:
            return None

        fig, ax1 = plt.subplots()

        ax1.set_title(title, fontsize=16)
        ax1.set_xlabel('Brand', fontsize=12)
        ax1.set_ylabel(ylabel if chart_type == 'bar' else 'Share of Sales', fontsize=12)

        if chart_type == 'bar':
            ax1.bar(x, y1, label='Quantity Sold', color='blue')
            ax2 = ax1.twinx()
            ax2.plot(x, y2, color='red', marker='o', label='Total Revenue')
            ax2.set_ylabel('Total Revenue', fontsize=12)
            ax2.legend(loc='upper right')
        elif chart_type == 'pie':
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['blue', 'orange', 'green', 'red'])
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    except Exception as e:
        print(f"Error in create_plot: {e}")
        return None

def create_line_chart(category, item):
    try:
        filtered_data = df[(df['category'] == category) & (df['item'] == item)]

        if filtered_data.empty:
            return None

        fig, ax = plt.subplots()
        filtered_data.groupby('month')['quantity_sold'].sum().plot(kind='line', ax=ax, marker='o', color='green')
        
        ax.set_title(f'Monthly Sales Trend for {item} in {category}')
        ax.set_xlabel('Month')
        ax.set_ylabel('Quantity Sold')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    except Exception as e:
        print(f"Error in create_line_chart: {e}")
        return None

def create_stacked_bar_chart(category, item):
    try:
        filtered_data = df[(df['category'] == category) & (df['item'] == item)]

        if filtered_data.empty:
            return None

        plot_data = filtered_data.groupby(['brand', 'month']).agg({'quantity_sold': 'sum'}).unstack().fillna(0)
        plot_data.columns = plot_data.columns.droplevel()

        ax = plot_data.plot(kind='bar', stacked=True, colormap='viridis')

        ax.set_title(f'Monthly Sales Breakdown for {item} in {category}')
        ax.set_xlabel('Month')
        ax.set_ylabel('Quantity Sold')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    except Exception as e:
        print(f"Error in create_stacked_bar_chart: {e}")
        return None

def create_monthly_line_chart(category, item):
    try:
        filtered_data = df[(df['category'] == category) & (df['item'] == item)]

        if filtered_data.empty:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        filtered_data.groupby(['month', 'brand'])['quantity_sold'].sum().unstack().plot(ax=ax, marker='o')

        ax.set_title(f'Monthly Sales Trend for {item} in {category}')
        ax.set_xlabel('Month')
        ax.set_ylabel('Quantity Sold')
        ax.legend(title='Brand', bbox_to_anchor=(1.05, 1), loc='upper left')

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        plt.close()

        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    except Exception as e:
        print(f"Error in create_monthly_line_chart: {e}")
        return None

def get_insights(category, item, month, chart_type):
    insights = []

    if chart_type == 'bar':
        best_selling_brand = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)].groupby('brand')['quantity_sold'].sum().idxmax()
        total_sales = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)]['quantity_sold'].sum()
        total_revenue = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)]['price'].sum()

        insights.append(f"Bestselling brand for {item} in {category} - {month}: {best_selling_brand}")
        insights.append(f"Total sales for {item} in {category} - {month}: {total_sales}")
        insights.append(f"Total revenue for {item} in {category} - {month}: ${total_revenue:.2f}")
    elif chart_type == 'pie':
        best_selling_brand = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)].groupby('brand')['quantity_sold'].sum().idxmax()
        total_sales = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)]['quantity_sold'].sum()
        total_revenue = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)]['price'].sum()

        insights.append(f"Bestselling brand for {item} in {category} - {month}: {best_selling_brand}")
        insights.append(f"Total sales for {item} in {category} - {month}: {total_sales}")
        insights.append(f"Total revenue for {item} in {category} - {month}: ${total_revenue:.2f}")
    elif chart_type == 'line':
        total_sales = df[(df['category'] == category) & (df['item'] == item)]['quantity_sold'].sum()
        total_revenue = df[(df['category'] == category) & (df['item'] == item)]['price'].sum()

        insights.append(f"Total sales for {item} in {category}: {total_sales}")
        insights.append(f"Total revenue for {item} in {category}: ${total_revenue:.2f}")
    elif chart_type == 'stacked_bar':
        best_selling_brand = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)].groupby('brand')['quantity_sold'].sum().idxmax()
        total_sales = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)]['quantity_sold'].sum()
        total_revenue = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)]['price'].sum()

        insights.append(f"Bestselling brand for {item} in {category} - {month}: {best_selling_brand}")
        insights.append(f"Total sales for {item} in {category} - {month}: {total_sales}")
        insights.append(f"Total revenue for {item} in {category} - {month}: ${total_revenue:.2f}")
    elif chart_type == 'monthly_line':
        total_sales = df[(df['category'] == category) & (df['item'] == item)]['quantity_sold'].sum()
        total_revenue = df[(df['category'] == category) & (df['item'] == item)]['price'].sum()

        insights.append(f"Total sales for {item} in {category}: {total_sales}")
        insights.append(f"Total revenue for {item} in {category}: ${total_revenue:.2f}")

    return insights

@app.route('/generate_plot', methods=['POST'])
def generate_plot():
    category = request.form['category']
    item = request.form['item']
    month = request.form['month']
    chart_type = request.form['chart_type']

    if chart_type == 'line':
        plot_data = create_line_chart(category, item)
    elif chart_type == 'stacked_bar':
        plot_data = create_stacked_bar_chart(category, item)
    elif chart_type == 'monthly_line':
        plot_data = create_monthly_line_chart(category, item)
    else:
        plot_data = create_plot(category, item, month, chart_type)

    insights = get_insights(category, item, month, chart_type)

    # Calculate and display skewness
    skew_value = calculate_skew(category, item, month)
    insights.append(f"Skewness of Sales for {item} in {category} - {month}: {skew_value:.2f}")

    max_sales_month = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)]['month'].value_counts().idxmax()

    item_status_insight = assess_item_status(category, item,max_sales_month)
    return render_template('result.html', plot_data=plot_data, insights=insights,item_status_insight = item_status_insight)

def calculate_skew(category, item, month):
    try:
        filtered_data = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == month)]
        skewness = skew(filtered_data['quantity_sold'])
        return skewness
    except Exception as e:
        print(f"Error in calculate_skew: {e}")
        return None
    
# def generate_predictions(category, item, current_month):
#     try:
#         # Assuming your data has a 'month' column in a date format
#         next_month = pd.to_datetime(current_month) + pd.DateOffset(months=1)

#         # Filter data for the next month
#         next_month_data = df[(df['category'] == category) & (df['item'] == item) & (df['month'] == next_month)]

#         # Calculate skewness of the sales for the current item and category
#         current_data = df[(df['category'] == category) & (df['item'] == item)]
#         current_skewness = skew(current_data['quantity_sold'])

#         # Make predictions based on the current skewness
#         if current_skewness < -0.5:
#             prediction = "Sales are likely declining."
#         elif -0.5 <= current_skewness <= 0.5:
#             prediction = "Sales are relatively stable."
#         else:
#             prediction = "Sales are likely increasing."

#         predictions = [
#             f"Skewness of Sales for {item} in {category}: {current_skewness:.2f}",
#             f"Prediction: {prediction}"
#         ]

#         return predictions

#     except Exception as e:
#         print(f"Error in generate_predictions: {e}")
#         return []

if __name__ == '__main__':
    app.run(debug=True)
