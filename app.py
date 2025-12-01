import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64

# 页面设置
st.set_page_config(
    page_title="Excel价格核对工具 - 云端版",
    page_icon="📱",
    layout="wide"
)

# 应用标题
st.title("📱 Excel价格核对工具 - 云端版")
st.markdown("**无需安装，在线使用 | 支持多人在线协作**")
st.markdown("---")

# 颜色映射规则
COLOR_MAPPING = {
    'Midnight': 'black',
    'Space Black': 'black', 
    'Graphite': 'black',
    'Starlight': 'White',
    'Silver': 'White',
    'Pacific Blue': 'Blue',
    'Sierra Blue': 'Blue',
    'Blue': 'Blue',
    'Deep Purple': 'purple',
    'Alpine Green': 'Green',
    'Green': 'Green'
}

def get_download_link(df, filename, link_text):
    """生成下载链接"""
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def normalize_color(color):
    """标准化颜色名称"""
    if pd.isna(color):
        return color
    return COLOR_MAPPING.get(str(color), str(color))

def normalize_grade(grade):
    """标准化等级名称"""
    if pd.isna(grade):
        return grade
    grade_str = str(grade)
    if 'B+' in grade_str:
        return 'B+'
    return grade_str

def process_files(file_a, file_b):
    """处理两个Excel文件"""
    try:
        # 读取Excel文件
        if file_a.name.endswith('.csv'):
            df_a = pd.read_csv(file_a)
        else:
            df_a = pd.read_excel(file_a)
        
        if file_b.name.endswith('.csv'):
            df_b = pd.read_csv(file_b)
        else:
            df_b = pd.read_excel(file_b)
        
        # 显示文件预览
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 表A预览（前5行）")
            st.dataframe(df_a.head())
        
        with col2:
            st.subheader("📋 表B预览（前5行）")
            st.dataframe(df_b.head())
        
        # 自动检测列名
        st.subheader("🔍 自动检测列名")
        
        # 查找可能的列名
        def find_column(df, keywords):
            for col in df.columns:
                for keyword in keywords:
                    if keyword.lower() in str(col).lower():
                        return col
            return df.columns[0]  # 默认返回第一列
        
        # 自动检测
        model_col_a = find_column(df_a, ['model', '型号', 'Model'])
        capacity_col_a = find_column(df_a, ['gb', '容量', 'storage', '容量'])
        grade_col_a = find_column(df_a, ['grade', '等级', '级别'])
        price_col_a = find_column(df_a, ['價格', '价格', 'price', '基础价格'])
        
        model_col_b = find_column(df_b, ['model', '型号', 'Model'])
        capacity_col_b = find_column(df_b, ['capacity', '容量', '存储', 'gb'])
        grade_col_b = find_column(df_b, ['grade', '等级', '级别'])
        color_col_b = find_column(df_b, ['color', '颜色', 'colour'])
        bid_price_col_b = find_column(df_b, ['bid', 'price', '报价', '价格', 'bid price'])
        
        # 显示自动检测结果
        st.info(f"""
        **自动检测结果：**
        - **表A**: 型号→{model_col_a} | 容量→{capacity_col_a} | 等级→{grade_col_a} | 价格→{price_col_a}
        - **表B**: 型号→{model_col_b} | 容量→{capacity_col_b} | 等级→{grade_col_b} | 颜色→{color_col_b} | 报价→{bid_price_col_b}
        """)
        
        # 用户确认或修改
        with st.expander("⚙️ 手动调整列映射（可选）"):
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            with col_a1:
                model_col_a = st.selectbox("表A-型号列", df_a.columns, list(df_a.columns).index(model_col_a))
            with col_a2:
                capacity_col_a = st.selectbox("表A-容量列", df_a.columns, list(df_a.columns).index(capacity_col_a))
            with col_a3:
                grade_col_a = st.selectbox("表A-等级列", df_a.columns, list(df_a.columns).index(grade_col_a))
            with col_a4:
                price_col_a = st.selectbox("表A-价格列", df_a.columns, list(df_a.columns).index(price_col_a))
            
            col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
            with col_b1:
                model_col_b = st.selectbox("表B-型号列", df_b.columns, list(df_b.columns).index(model_col_b))
            with col_b2:
                capacity_col_b = st.selectbox("表B-容量列", df_b.columns, list(df_b.columns).index(capacity_col_b))
            with col_b3:
                grade_col_b = st.selectbox("表B-等级列", df_b.columns, list(df_b.columns).index(grade_col_b))
            with col_b4:
                color_col_b = st.selectbox("表B-颜色列", df_b.columns, list(df_b.columns).index(color_col_b))
            with col_b5:
                bid_price_col_b = st.selectbox("表B-报价列", df_b.columns, list(df_b.columns).index(bid_price_col_b))
        
        if st.button("🚀 开始核对价格", type="primary", use_container_width=True):
            with st.spinner("正在处理数据..."):
                # 处理数据
                df_a_processed = df_a.copy()
                df_b_processed = df_b.copy()
                
                # 标准化颜色和等级
                df_b_processed['Normalized_Color'] = df_b_processed[color_col_b].apply(normalize_color)
                df_b_processed['Normalized_Grade'] = df_b_processed[grade_col_b].apply(normalize_grade)
                
                # 确保容量为字符串
                df_a_processed[capacity_col_a] = df_a_processed[capacity_col_a].astype(str)
                df_b_processed[capacity_col_b] = df_b_processed[capacity_col_b].astype(str)
                
                # 标准化容量（1TB → 1000GB）
                def standardize_capacity(cap):
                    if pd.isna(cap):
                        return cap
                    cap_str = str(cap).upper().replace(' ', '')
                    if 'TB' in cap_str:
                        num = ''.join(filter(str.isdigit, cap_str))
                        if num:
                            return f"{int(num) * 1000}GB"
                    return cap_str
                
                df_a_processed['Std_Capacity'] = df_a_processed[capacity_col_a].apply(standardize_capacity)
                df_b_processed['Std_Capacity'] = df_b_processed[capacity_col_b].apply(standardize_capacity)
                
                # 开始核对
                results = []
                
                for idx, row_b in df_b_processed.iterrows():
                    # 查找表A中匹配的行
                    mask = (
                        (df_a_processed[model_col_a] == row_b[model_col_b]) &
                        (df_a_processed['Std_Capacity'] == row_b['Std_Capacity'])
                    )
                    
                    matched_rows = df_a_processed[mask]
                    
                    if len(matched_rows) == 0:
                        results.append({
                            '状态': '❌ 未找到匹配',
                            '表B行号': idx + 2,
                            '型号': row_b[model_col_b],
                            '容量': row_b[capacity_col_b],
                            '颜色': row_b[color_col_b],
                            '等级': row_b[grade_col_b],
                            'BID报价': row_b[bid_price_col_b],
                            '预期价格': 'N/A',
                            '差异': 'N/A',
                            '备注': '表A中无匹配型号/容量'
                        })
                        continue
                    
                    # 按等级过滤
                    grade_matched = []
                    for _, row_a in matched_rows.iterrows():
                        if normalize_grade(row_a[grade_col_a]) == row_b['Normalized_Grade']:
                            grade_matched.append(row_a)
                    
                    if len(grade_matched) == 0:
                        results.append({
                            '状态': '❌ 等级不匹配',
                            '表B行号': idx + 2,
                            '型号': row_b[model_col_b],
                            '容量': row_b[capacity_col_b],
                            '颜色': row_b[color_col_b],
                            '等级': row_b[grade_col_b],
                            'BID报价': row_b[bid_price_col_b],
                            '预期价格': 'N/A',
                            '差异': 'N/A',
                            '备注': f'表A中无匹配等级: {row_b[grade_col_b]}'
                        })
                        continue
                    
                    # 计算预期价格（简化版逻辑）
                    row_a = grade_matched[0]
                    expected_price = '需手动计算'
                    diff = 'N/A'
                    status = '⚠️ 需检查'
                    
                    # 这里添加你的价格计算逻辑
                    # 由于你的计算逻辑较复杂，这里简化处理
                    results.append({
                        '状态': status,
                        '表B行号': idx + 2,
                        '型号': row_b[model_col_b],
                        '容量': row_b[capacity_col_b],
                        '颜色': row_b[color_col_b],
                        '等级': row_b[grade_col_b],
                        'BID报价': row_b[bid_price_col_b],
                        '预期价格': expected_price,
                        '差异': diff,
                        '备注': '价格计算逻辑需在云端完整实现'
                    })
                
                # 显示结果
                results_df = pd.DataFrame(results)
                
                # 统计
                total = len(results_df)
                error_count = len(results_df[results_df['状态'].str.contains('❌')])
                warning_count = len(results_df[results_df['状态'].str.contains('⚠️')])
                success_count = total - error_count - warning_count
                
                # 显示统计卡片
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总行数", total)
                with col2:
                    st.metric("成功匹配", success_count, delta=f"{success_count/total*100:.1f}%")
                with col3:
                    st.metric("问题行数", error_count + warning_count, delta_color="inverse")
                
                # 显示详细结果
                st.subheader("📋 详细核对结果")
                st.dataframe(results_df, use_container_width=True)
                
                # 下载按钮
                st.markdown(get_download_link(results_df, "核对结果.csv", "📥 下载核对结果(CSV)"), unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"处理文件时出错: {str(e)}")
        st.exception(e)

# 主界面
st.sidebar.header("📂 上传文件")

# 文件上传组件
file_a = st.sidebar.file_uploader(
    "上传价格标准表（表A）",
    type=['xlsx', 'xls', 'csv'],
    help="支持Excel和CSV格式"
)

file_b = st.sidebar.file_uploader(
    "上传待核对表（表B）",
    type=['xlsx', 'xls', 'csv'],
    help="支持Excel和CSV格式"
)

# 使用说明
with st.sidebar.expander("📖 使用说明", expanded=True):
    st.markdown("""
    ### 快速开始：
    1. **上传两个Excel文件**
    2. **系统自动检测列名**
    3. **点击开始核对**
    4. **下载结果报告**
    
    ### 支持功能：
    - 自动列名识别
    - 颜色标准化
    - 容量单位转换
    - 批量数据处理
    
    ### 文件要求：
    - 文件大小：≤200MB
    - 格式：Excel (.xlsx, .xls) 或 CSV
    - 编码：UTF-8（推荐）
    """)

# 主内容区
if file_a is not None and file_b is not None:
    process_files(file_a, file_b)
else:
    st.info("👈 请从左侧上传两个Excel/CSV文件")
    
    # 显示示例文件下载
    with st.expander("📥 下载示例文件"):
        # 创建示例数据
        sample_a = pd.DataFrame({
            'Model': ['iPhone 12', 'iPhone 13'],
            'GB': ['64GB', '128GB'],
            'Grade': ['DLS B+', 'TPS B+'],
            '價格': [123, 202],
            'Red': [-3, -3],
            'White': [1, 1]
        })
        
        sample_b = pd.DataFrame({
            'Model': ['iPhone 12', 'iPhone 13'],
            'Capacity': ['64GB', '128GB'],
            'Color': ['Red', 'White'],
            'Grade': ['DLS B+', 'TPS B+'],
            'Bid Price': [120, 203]
        })
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(get_download_link(sample_a, "示例_价格标准表.csv", "下载表A示例"), unsafe_allow_html=True)
        with col2:
            st.markdown(get_download_link(sample_b, "示例_待核对表.csv", "下载表B示例"), unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.caption("✨ Excel价格核对工具云端版 | 数据仅在本次会话中处理，不会保存到服务器")
