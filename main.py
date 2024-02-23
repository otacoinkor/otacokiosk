# streamlit run Z:\work\python\streamlit_test\main.py
# 정지는 ctrl + c

import streamlit as st
import pandas as pd
import pymysql
import config


@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    datf = [input_df.loc[i: i + rows - 1, :] for i in range(0, len(input_df), rows)]
    return datf


st.set_page_config(layout="wide")

with st.sidebar:
    st.title('메뉴 1')
    st.title('메뉴 2')
    st.title('메뉴 3')

connection = pymysql.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)

print('connected')

cursor = connection.cursor()

cursor.execute("Select * from _PickPic_Log_Magok")
data = cursor.fetchall()
column_names = [desc[0] for desc in cursor.description]
print(column_names)

dataset = pd.DataFrame(data, columns=column_names)

st.title("요소수 관리자 OTACO")

top_menu = st.columns(3)
with top_menu[0]:
    sort = st.radio("Sort Data", options=["Yes", "No"], horizontal=1, index=1)
if sort == "Yes":
    with top_menu[1]:
        sort_field = st.selectbox("Sort By", options=dataset.columns)
    with top_menu[2]:
        sort_direction = st.radio(
            "Direction", options=["⬆️", "⬇️"], horizontal=True
        )
    dataset = dataset.sort_values(
        by=sort_field, ascending=sort_direction == "⬆️", ignore_index=True
    )
pagination = st.container()

bottom_menu = st.columns((4, 1, 1))
with bottom_menu[2]:
    batch_size = st.selectbox("Page Size", options=[25, 50, 100])
with bottom_menu[1]:
    total_pages = (
        int(len(dataset) / batch_size) if int(len(dataset) / batch_size) > 0 else 1
    )
    current_page = st.number_input(
        "Page", min_value=1, max_value=total_pages, step=1
    )
with bottom_menu[0]:
    st.markdown(f"Page **{current_page}** of **{total_pages}** ")

pages = split_frame(dataset, batch_size)
pagination.dataframe(data=pages[current_page - 1], use_container_width=True)

# 수정할 라인과 필드를 선택하는 위젯 추가
edit_menu = st.columns((3, 3, 3))
with edit_menu[0]:
    line_to_edit = st.selectbox("Select Line to Edit", options=dataset['kiosk_id'].tolist())
with edit_menu[1]:
    field_to_edit = st.selectbox("Select Field to Edit", options=column_names)


# 수정할 값을 입력하는 위젯 추가
with edit_menu[2]:
    new_value = st.text_input("Enter New Value")

# 값 수정 버튼 추가
if st.button("Submit Changes"):
    dataset.loc[line_to_edit, field_to_edit] = new_value
    # SQL 쿼리를 생성합니다. 이때, 필드와 라인은 사용자가 선택한 것을 기반으로 합니다.
    sql_query = f"UPDATE _PickPic_Log_Magok SET {field_to_edit} = '{new_value}' WHERE kiosk_id = {line_to_edit}"
    # SQL 쿼리를 실행하여 데이터베이스를 업데이트합니다.
    cursor.execute(sql_query)
    # 변경사항을 데이터베이스에 반영합니다.
    connection.commit()
    st.write("Changes submitted.")
