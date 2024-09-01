import tkinter as tk
import psycopg2
import datetime
from tkinter import messagebox

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Todoリスト")

        #編集対象データ辞書
        self.selected={"selected_data":"","selected_listid":""}

        self.frames={}

        for F in (StartPage,SearchPage,EditPage):
            frame=F(self)
            self.frames[F]=frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.geometry("400x500")

        #メニューバーの作成
        self.menubar=tk.Menu(self)
        self.menu1=tk.Menu(self,tearoff=False)
        self.menu1.add_command(label="検索",command=lambda:self.show_frame(SearchPage))
        self.menu1.add_command(label="保存",command=lambda:self.save())
        self.menu1.add_command(label="削除",command=lambda:self.delete())
        self.menubar.add_cascade(label="メニュー",menu=self.menu1)
        self.menu1.entryconfig("保存",state="disabled")
        self.menu1.entryconfig("削除",state="disabled")
        self.config(menu=self.menubar)

        self.show_frame(StartPage)
    
    def show_frame(self,cont):
        frame=self.frames[cont]
        frame.tkraise()
        self.current_frame=frame
        frame.update_data()

    def save(self):
        #【新規登録】新規作成画面での保存
        if isinstance(self.current_frame,StartPage):
            if messagebox.askokcancel("ok/cancel","保存します"):
                try:
                    conn = psycopg2.connect(
                        host="localhost",
                        database="todolistdatabase",
                        user="todouser",
                        password="todopass"
                    )
                    # 日付の取得
                    current=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cur = conn.cursor()

                    # 全テキストボックスから内容を取得
                    start_page = self.frames[StartPage]
                    texts_to_insert = [text.get("1.0", "end-1c") for text in start_page.text_boxes]
                    
                    # リストIDを採番
                    cur.execute("""
                        INSERT INTO listid (ins_date)
                        VALUES (%s);
                    """, (current,))

                    # リストIDを取得
                    cur.execute("SELECT list_id FROM listid WHERE ins_date = %s;",(current,))
                    
                    # 取得したデータをフェッチ
                    list_id = cur.fetchall()
                    
                    # 取得したデータを表示
                    for row in list_id:
                        todolist_id=row

                    # リスト内容(タスク)の登録
                    for text in texts_to_insert:
                        
                        if text.strip():
                            cur.execute("""
                                INSERT INTO todolist (thingstodo, ins_date, name, todolist_id)
                                VALUES (%s, %s, 'testuser', %s)
                            """, (text, current, todolist_id))

                    conn.commit()
                    cur.close()
                    conn.close()
                    messagebox.showinfo(title="",message="登録完了")
                except Exception as e:
                    print(e.args)
                    messagebox.showerror(title=None, message="DB更新に失敗しました")
                # テキストボックスをクリア
                start_page.clear_text_boxes()
                # 保存ボタンを無効にする
                self.menu1.entryconfig("保存", state="disabled")
                
                # 表示されているフレームを更新
                self.show_frame(StartPage)

        #【更新】編集画面での保存
        else:
            if messagebox.askokcancel("ok/cancel","保存します"):
                try:
                    conn = psycopg2.connect(
                        host="localhost",
                        database="todolistdatabase",
                        user="todouser",
                        password="todopass"
                    )
                    # 日付の取得
                    current=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cur = conn.cursor()

                    # 更新対象のTodolist ID
                    list_id=self.selected['selected_listid']

                    # 全テキストボックスから内容を取得
                    edit_page = self.frames[EditPage]
                    texts_to_insert = [text.get("1.0", "end-1c") for text in edit_page.text_boxes]
                    
                    # 取得したデータの削除フラグを0->1に更新
                    update_query = """
                        UPDATE todolist 
                        SET delflg = '1', 
                            upd_date = %s
                        WHERE todolist_id=%s
                        """
                    cur.execute(update_query, (current,list_id,))

                    # リスト内容(タスク)の登録
                    for text in texts_to_insert:
                        
                        if text.strip():
                            cur.execute("""
                                INSERT INTO todolist (thingstodo, ins_date, name, todolist_id)
                                VALUES (%s, %s, 'testuser', %s)
                            """, (text, current, list_id))

                    conn.commit()
                    cur.close()
                    conn.close()
                    messagebox.showinfo(title="",message="登録完了")
                except Exception as e:
                    print(e.args)
                    conn.rollback()
                    messagebox.showerror(title=None, message="DB更新に失敗しました")
                # テキストボックスをクリア
                edit_page.clear_text_boxes()
                # 保存ボタンを無効にする
                self.menu1.entryconfig("保存", state="disabled")
                
                # 表示されているフレームを更新
                self.show_frame(StartPage)

    def delete(self):
        if messagebox.askokcancel("ok/cancel","削除してもよろしいですか？"):
            #データ削除SQL
            print('削除')
        

    

class StartPage(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        
        self.add_buttons_frame = tk.Frame(self)
        self.add_buttons_frame.grid(column=1, row=2, padx=10, pady=10, sticky="ew")

        self.text_boxes = []

        self.add_button = tk.Button(self, text="+", command=self.button_ins_pushed)
        self.add_button.grid(column=1, row=1, padx=10, pady=10, sticky="w")

    def button_ins_pushed(self):
        index = len(self.text_boxes)
        text = tk.Text(self.add_buttons_frame, height=1, width=30)
        text.grid(row=index, column=0, padx=5, pady=5)
        self.text_boxes.append(text)
        app.menu1.entryconfig("保存",state="normal")
    
    def update_data(self):
        pass

    def clear_text_boxes(self):
        for i in range(len(self.text_boxes)):
            # ウィジェットを削除
            self.text_boxes[i].destroy()
        self.text_boxes = []            

class SearchPage(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent

        tk.Label(self,text="編集するデータを選択してください").grid(padx=10, pady=10,sticky="w")
        
        self.listbox = tk.Listbox(self,width=50,height=20)
        self.listbox.grid(padx=10, pady=10)

        button1 = tk.Button(self, text="選択を確定し、Edit Pageへ進む",
                            command=self.confirm_selection)
        button1.grid()

        button2 = tk.Button(self,text="戻る",command=self.goback)
        button2.grid(padx=10, pady=10,sticky="w")

    def confirm_selection(self):
        app.menu1.entryconfig("保存",state="normal")
        if not self.listbox.curselection():
            messagebox.showwarning(title="未選択",message="どれか1つの\nリストを選択してください")
        else:
            selection=self.listbox.get(self.listbox.curselection()).split()
            self.parent.selected['selected_data']=selection[1]
            self.parent.selected['selected_listid']=selection[0]
            self.parent.show_frame(EditPage)
    
    def goback(self):
        self.parent.show_frame(StartPage)

    def update_data(self):

        app.menu1.entryconfig("保存",state="disabled")
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="todolistdatabase",
                user="todouser",
                password="todopass"
            )
            cur = conn.cursor()

            # リストIDを取得
            cur.execute("""
                        select li.todolist_id,count(*),li.name,li.ins_date
                        from todolist as li
                        where li.todolist_id is not null AND delflg = '0'
                        group by li.todolist_id,li.name,li.ins_date
                        order by li.ins_date;
                        """)
            
            # 取得したデータをフェッチ
            list_rc = cur.fetchall()
            self.listbox.delete(0,tk.END)
            # 取得したデータを表示
            i=0
            for row in list_rc:
                # 編集ページで参照するためのデータ
                self.listbox.insert(i, row[0]+"     "+str(row[1])+"     "+row[2]+"     "+str(row[3]))
                i=i+1

            cur.close()
            conn.close()

        except Exception as e:
            print(e.args)
            messagebox.showerror(title=None, message="DB検索に失敗しました")

class EditPage(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent

        self.add_button = tk.Button(self, text="+", command=self.button_ins_pushed)
        self.add_button.grid(column=0, row=1, padx=10, pady=10, sticky="w")

        self.text_boxes = []
        self.add_buttons_frame = tk.Frame(self)
        self.add_buttons_frame.grid(column=1, row=2, padx=10, pady=10, sticky="ew")
        
        button = tk.Button(self,text="戻る",command=self.goback)
        button.grid(padx=10, pady=10)

    def button_ins_pushed(self):
        index = len(self.text_boxes)
        text = tk.Text(self.add_buttons_frame, height=1, width=30)
        text.grid(row=index, column=0, padx=5, pady=5)
        self.text_boxes.append(text)

    def update_data(self):
        for i in range(len(self.text_boxes)):
            # ウィジェットを削除
            self.text_boxes[i].destroy()
        self.text_boxes = []
        num_txt=int(self.parent.selected['selected_data'])
        list_id=self.parent.selected['selected_listid']

        # タスク一覧を取得し、テキストボックスにはめる
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="todolistdatabase",
                user="todouser",
                password="todopass"
            )
            cur = conn.cursor()

            # リストIDを取得
            cur.execute("""
                        select li.thingstodo
                        from todolist as li
                        where li.todolist_id = %s and li.delflg = '0'
                        order by li.id
                        ;
                        """,(list_id,))

            # 取得したデータをフェッチ
            list_rc = cur.fetchall()
            # 取得したデータを表示
            i=0
            data=[]
            for row in list_rc:
                # 編集ページで参照するためのデータ
                i=i+1
                data.append(row[0])

            cur.close()
            conn.close()

            for i in range(num_txt):
                text = tk.Text(self.add_buttons_frame, height=1, width=30)
                text.grid(row=i, column=0, padx=5, pady=5)
                initial_text = data[i]
                text.insert("1.0", initial_text)
                self.text_boxes.append(text)

        except Exception as e:
            print(e.args)
            messagebox.showerror(title=None, message="DB検索に失敗しました")

    def goback(self):
        self.parent.show_frame(SearchPage)
    
    def clear_text_boxes(self):
        for i in range(len(self.text_boxes)):
            # ウィジェットを削除
            self.text_boxes[i].destroy()
        self.text_boxes = []

if __name__ =='__main__':
    app=App()
    app.mainloop()    

        