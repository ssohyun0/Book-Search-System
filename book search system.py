#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pandas as pd
import networkx as nx
import tkinter as tk
from tkinter import messagebox, ttk
import warnings
from collections import deque
import threading

warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl')

file_path = '/Users/jangsohyun/Desktop/도서검색/list.xlsx'
df = pd.read_excel(file_path)

# 큐를 사용하여 최근 본 도서 5개를 저장
recently_viewed = deque(maxlen=5)

# 그래프 생성 및 유사도 기반 간선 추가
G = nx.Graph()

def create_graph():
    for i, row in df.iterrows():
        G.add_node(row['상품명'])
        for j, row2 in df.iterrows():
            if i != j:
                similarity = len(set(row['분야'].split(', ')) & set(row2['분야'].split(', ')))
                if similarity > 0:
                    G.add_edge(row['상품명'], row2['상품명'], weight=similarity)

threading.Thread(target=create_graph).start()

# 도서 검색 함수
def search_books(book_name=''):
    result = df
    if book_name:
        result = result[result['상품명'].str.contains(book_name, case=False, na=False)]
    return result

# 도서 추천 함수
def recommend_books(title):
    if title not in G:
        return []
    neighbors = sorted(G[title], key=lambda x: G[title][x]['weight'], reverse=True)
    return neighbors[:5]

# 큐에 저장된 도서명을 기반으로 추천 도서 제공 함수
def recommend_books_from_queue():
    recommendations = []
    for book in recently_viewed:
        recommendations.extend(recommend_books(book))
    # 중복 제거 및 상위 5개 도서 반환
    recommendations = list(dict.fromkeys(recommendations))
    return recommendations[:5]

# 도서 정렬 함수
def sort_books(dataframe, criteria):
    return dataframe.sort_values(by=criteria)

# 검색된 도서 제목만 표시하는 함수
def display_book_titles(books):
    for widget in book_frame.winfo_children():
        widget.destroy()
    
    canvas = tk.Canvas(book_frame)
    scrollbar = tk.Scrollbar(book_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    if books.empty:
        message_label = tk.Label(scrollable_frame, text="검색 결과가 없습니다")
        message_label.pack()
    else:
        for index, book in books.iterrows():
            book_button = tk.Button(scrollable_frame, text=book['상품명'], command=lambda b=book['상품명']: view_and_store_book(b))
            book_button.pack()
        home_button = tk.Button(scrollable_frame, text="홈으로 돌아가기", command=show_home)
        home_button.pack()

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def view_and_store_book(title):
    recently_viewed.appendleft(title)
    show_book_details(df[df['상품명'] == title])

# 도서 상세 정보 표시 함수
def show_book_details(book):
    for widget in book_frame.winfo_children():
        widget.destroy()
    
    if not book.empty:
        for index, book in book.iterrows():
            details = f"제목: {book['상품명']}\n저자: {book['인물']}\n출판사: {book['출판사']}\n발행일: {book['발행(출시)일자']}\n가격: {book['판매가']}"
            book_label = tk.Label(book_frame, text=details)
            book_label.pack()
        
        # 유사한 도서 추천
        recommendations = recommend_books(book.iloc[0]['상품명'])
        recommended_books = df[df['상품명'].isin(recommendations)]
        if not recommended_books.empty:
            recommend_label = tk.Label(book_frame, text="유사한 도서 추천:")
            recommend_label.pack()
            for index, rec_book in recommended_books.iterrows():
                rec_button = tk.Button(book_frame, text=rec_book['상품명'], command=lambda b=rec_book['상품명']: view_and_store_book(b))
                rec_button.pack()
    
    home_button = tk.Button(book_frame, text="홈으로 돌아가기", command=show_home)
    home_button.pack()

def show_home():
    for widget in book_frame.winfo_children():
        widget.destroy()
    
    sort_label = tk.Label(book_frame, text="정렬 기준:")
    sort_label.pack()

    sort_criteria.set("인기순")
    sort_menu = ttk.Combobox(book_frame, textvariable=sort_criteria, values=["인기순", "가격순", "발행일순"])
    sort_menu.pack()

    book_name_label = tk.Label(book_frame, text="도서명:")
    book_name_label.pack()

    book_name_entry.pack()

    search_button.pack()

    recent_books = list(recently_viewed)
    if recent_books:
        recent_label = tk.Label(book_frame, text="최근에 검색한 도서:")
        recent_label.pack()
        for book in recent_books:
            book_button = tk.Button(book_frame, text=book, command=lambda b=book: show_book_details(df[df['상품명'] == b]))
            book_button.pack()
    
    recommended_books = recommend_books_from_queue()
    if recommended_books:
        recommended_label = tk.Label(book_frame, text="추천 도서:")
        recommended_label.pack()
        for book in recommended_books:
            rec_book = df[df['상품명'] == book].iloc[0]
            rec_button = tk.Button(book_frame, text=rec_book['상품명'], command=lambda b=rec_book['상품명']: view_and_store_book(b))
            rec_button.pack()

# GUI 구현
root = tk.Tk()
root.title('도서 추천 시스템')

# GUI 레이아웃 설정
sort_criteria = tk.StringVar()

book_name_entry = tk.Entry(root)

search_button = tk.Button(root, text="검색", command=lambda: display_book_titles(sort_books(search_books(book_name_entry.get()), '상품명')))

book_frame = tk.Frame(root)
book_frame.pack(fill="both", expand=True)

def display_books(books):
    if books.empty:
        show_book_details(pd.DataFrame())
    else:
        show_book_details(books)

# 초기 홈 화면 표시
show_home()

root.mainloop()


# In[ ]:




