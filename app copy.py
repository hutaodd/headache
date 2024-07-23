import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

# 加载数据
def load_data():
    try:
        data = pd.read_csv('headache_data.csv')
    except FileNotFoundError:
        data = pd.DataFrame(columns=['Date', 'Start Time', 'End Time', 'Duration', 'Severity', 'Remarks', 'Location'])
    return data

# 保存数据
def save_data(data):
    data.to_csv('headache_data.csv', index=False, encoding='utf-8-sig')

# 计算持续时间并格式化为小时分钟
def calculate_duration(start_time, end_time):
    duration = end_time - start_time
    total_minutes = duration.total_seconds() / 60  # 转换为分钟
    hours, minutes = divmod(total_minutes, 60)
    return f"{int(hours)}小时{int(minutes)}分钟", total_minutes

# 页面标题
st.title('头痛记录和可视化')

# 添加头痛记录
st.header('添加头痛记录')
with st.form('headache_form'):
    date = st.date_input('日期', datetime.now().date())
    start_time = st.time_input('头痛开始时间', datetime.now().time().replace(second=0, microsecond=0))
    end_time = st.time_input('头痛结束时间', datetime.now().time().replace(second=0, microsecond=0))
    severity = st.slider('严重程度', 1, 5, 1)
    remarks = st.text_area('备注')
    location = st.multiselect('头痛部位', ['左侧', '右侧', '双侧'])
    submitted = st.form_submit_button('添加记录')

    if submitted:
        try:
            start_datetime = datetime.combine(date, start_time)
            end_datetime = datetime.combine(date, end_time)
            duration, total_minutes = calculate_duration(start_datetime, end_datetime)
            location_str = ', '.join(location) if location else '未选择'
            new_record = pd.DataFrame([[date, start_datetime.strftime('%Y-%m-%d %H:%M'), end_datetime.strftime('%Y-%m-%d %H:%M'), duration, severity, remarks, location_str]],
                                      columns=['Date', 'Start Time', 'End Time', 'Duration', 'Severity', 'Remarks', 'Location'])
            data = load_data()
            data = pd.concat([data, new_record], ignore_index=True)
            save_data(data)
            st.success('记录已添加')
        except ValueError:
            st.error('时间格式错误，请检查输入时间')

# 显示头痛记录
st.header('头痛记录列表')
data = load_data()
if not data.empty:
    st.write(data)

# 数据可视化
st.header('数据可视化')
if not data.empty:
    data['Date'] = pd.to_datetime(data['Date'])

    # 头痛严重程度随时间变化的折线图
    chart1 = alt.Chart(data).mark_line().encode(
        x=alt.X('Date:T', axis=alt.Axis(format='%Y-%m-%d')),
        y='Severity:Q'
    ).properties(
        title='头痛严重程度随时间变化图'
    )
    st.altair_chart(chart1, use_container_width=True)

    # 按月份统计头痛次数的柱状图
    data['Month'] = data['Date'].dt.strftime('%Y-%m')
    month_counts = data['Month'].value_counts().reset_index()
    month_counts.columns = ['Month', 'Count']
    chart2 = alt.Chart(month_counts).mark_bar().encode(
        x='Month:O',
        y='Count:Q'
    ).properties(
        title='按月份统计头痛次数'
    )
    st.altair_chart(chart2, use_container_width=True)

    # 按星期几统计头痛次数的条形图
    data['Weekday'] = data['Date'].dt.day_name()
    weekday_counts = data['Weekday'].value_counts().reset_index()
    weekday_counts.columns = ['Weekday', 'Count']
    chart3 = alt.Chart(weekday_counts).mark_bar().encode(
        x='Weekday:O',
        y='Count:Q'
    ).properties(
        title='按星期几统计头痛次数'
    )
    st.altair_chart(chart3, use_container_width=True)

    # 头痛持续时间分布的柱状图
    data['Duration Minutes'] = data['Duration'].apply(
        lambda x: int(x.split('小时')[0]) * 60 + int(x.split('小时')[1].replace('分钟', ''))
    )
    bins = [0, 30, 60, 120, float('inf')]
    labels = ['0-30分钟', '30-60分钟', '60-120分钟', '120分钟以上']
    data['Duration Bin'] = pd.cut(data['Duration Minutes'], bins=bins, labels=labels, right=False)
    duration_counts = data['Duration Bin'].value_counts().reset_index()
    duration_counts.columns = ['Duration Bin', 'Count']
    chart4 = alt.Chart(duration_counts).mark_bar().encode(
        x='Duration Bin:O',
        y='Count:Q'
    ).properties(
        title='头痛持续时间分布'
    )
    st.altair_chart(chart4, use_container_width=True)

    # 按严重程度分布的饼图
    severity_counts = data['Severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    chart5 = alt.Chart(severity_counts).mark_arc().encode(
        theta='Count:Q',
        color='Severity:N'
    ).properties(
        title='按严重程度分布'
    )
    st.altair_chart(chart5, use_container_width=True)

# 提供数据下载功能
st.header('下载数据')
if not data.empty:
    csv = data.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="下载CSV",
        data=csv,
        file_name='headache_data.csv',
        mime='text/csv',
    )
