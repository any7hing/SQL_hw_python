import psycopg2
conn = psycopg2.connect(database='homework_db', user='postgres', password='9999')


def delete_tables():
    with conn.cursor() as cur:
        cur.execute("""
                drop table phone_numbers;
                drop table user_info;
                """)
    conn.commit()


def create_tables():
    with conn.cursor() as cur:
        cur.execute("""
                create table if not exists user_info(
                    id serial primary key,
                    first_name VARCHAR(40),
                    second_name VARCHAR(40),
                    email text NOT NULL
                );
                """)
        cur.execute("""
                create table if not exists phone_numbers(
                    id serial primary key,
                    user_id integer references user_info(id),
                    phone_number integer
                );
                """)
        conn.commit()


def create_user(first_name, second_name, email, phone=False):
    with conn.cursor() as cur:
        if phone is False:
            cur.execute("""
                insert into user_info(first_name,second_name,email)
                values(first_name=%s,second_name=%s,email=%s)
                """(first_name, second_name, email))
        else:
            cur.execute("""insert into user_info(first_name,second_name,email)
                values(%s,%s,%s) returning id""", (first_name, second_name, email))
            user_id = cur.fetchone()
            cur.execute("""
                        insert into phone_numbers(user_id,phone_number)
                        values(%s,%s)
                        """, (user_id[0], phone))
        print(f"Пользователь создан, его id {user_id}")
        conn.commit()


def get_user_id(email):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                        select id from user_info where email=%s
                        """, (email,))
            user_id = str(cur.fetchone()[0])
            return user_id
        except TypeError:
            return False


def add_phone_number(email, phone):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                        select id from user_info where email=%s
                        """, (email,))
            user_id = cur.fetchone()[0]
            cur.execute("""
                        insert into phone_numbers(user_id,phone_number)
                        values(%s,%s)
                        """, (user_id, phone))
        except TypeError:
            print("Неверные данные, пользователя не существует")
        conn.commit()


def chandge_user_data(email, **kwargs):
    with conn.cursor() as cur:
        user_id = get_user_id(email)
        if user_id is False: return print('Указанный email пользователя -  не существует')
        cur.execute("""
                    select id from user_info where email=%s
                    """, (email,))   
        for key in kwargs:
            cur.execute(f'update user_info set {key}=%s where id=%s', (f'{kwargs[key]}', user_id))
            conn.commit()
        print("Изменения внесены")


def delete_phone_number(email=None, phone=None):  # Если номер не указан, удаляет по id
    try:
        if phone is None:
            with conn.cursor() as cur:
                cur.execute("""
                        delete from phone_numbers where user_id = %s
                        """, (get_user_id(email))
                            )
                conn.commit()
                print('Номер удален')
        else:
            with conn.cursor() as cur:
                cur.execute("""
                        delete from phone_numbers where phone_number = %s
                        """, (phone,)
                            )
                conn.commit()
                print('Указанный номер удален')
    except TypeError:
        print('Неверные данные')


def delete_user(email):
    delete_phone_number(email=email)
    with conn.cursor() as cur:
        try:
            cur.execute("""
                        delete from user_info where id = %s
                        """, (get_user_id(email))
                        )
            print('Пользователь удален')
        except TypeError:
            print('Пользователя с указанными данными не существует')
    conn.commit()


def find_user(*args, **kwargs):
    with conn.cursor() as cur:
        for key in kwargs:
            cur.execute(f"select * from user_info where {key}=%s", (f'{kwargs[key]}',))
            res = cur.fetchall()
        if len(res):
            print(res)
        else:
            print('Пользователь не найден')


if __name__ == "__main__":
    # delete_tables()
    # create_tables()
    # create_user('Ivan', 'Ivanovich', 'ivan@mail.ru', 7777)
    # add_phone_number('ivan@mail.ru', 777)
    # chandge_user_data('Ivan@mail.ru', first_name="Vasya", second_name='Osel')  # ключ это поле которое меняем(first_name,second_name,email)
    # delete_phone_number('ivan@mail.ru')
    #delete_user('ivan@mail.ru')
    #find_user(first_name="Ivan", second_name="Ivanovich")
    conn.close()
