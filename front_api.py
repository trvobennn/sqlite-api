"""
This is an example of how end users could use the backend app to interface with sqlite database.

Simple REST type API.

This includes a get method, which allows for a generic sampling of table data,
a query for the database structure, and a set of 'WHERE' queries.
The second method is a post method. With post one can insert or update data.
Inserts can be done by one or by batch. Updates are one only.
Checks for basic errors and SQL injections.
"""


from backend import Database


class Front_api:
    def __init__(self, db_path, table_name):
        self.table_name = table_name
        self.db = Database(db_path,self.table_name)

    def get(self, url=None, payload=None):
        """for 'where' query, payload needs to be list or tuple of 2-3 items positioned correctly
        where payload ex - ['where_col','target','sign'] ...
        for 'where_fine' need where url with payload of either 4-5 items positioned correctly.
        where_fine = ['where_col','target', 'columns', 'sign', 'asc' (optional)]"""
        if url is None:
            self.db.tidy_print()
            return self.db.query_whole_table()
        if url == '/table':
            for prnt_table in self.db.get_table_info():
                print(prnt_table)
            return self.db.get_table_info()
        if url == '/where':
            if payload is None:
                raise ValueError('Invalid payload - needs to be at least 2 items')
            if len(payload) < 2 :
                raise ValueError('Invalid payload - needs to be at least 2 items')
            if isinstance(payload,tuple) or isinstance(payload,list):
                self.inj_check(payload[0])
                if isinstance(payload[1],str):
                    self.inj_check(payload[1])
                if len(payload) > 3:
                    for item in payload[2]:
                        if isinstance(item,str):
                            self.inj_check(item)
                    if len(payload[3]) > 3:
                        raise ValueError('Invalid comparison payload')
                    if len(payload) == 5:
                        if not isinstance(payload[4],bool):
                            raise ValueError('Invalid non-boolean payload')
                        return self.db.filter_fine_query(payload[0], payload[1], payload[2], sign=payload[3], asc=payload[4])
                    else:
                        return self.db.filter_fine_query(payload[0],payload[1],payload[2],sign=payload[3])
                if len(payload) == 3:
                    return self.db.filter_where_query(payload[0],target=payload[1],sign=payload[2])
                if len(payload) == 2:
                    return self.db.filter_where_query(payload[0],target=payload[1])
            else:
                raise ValueError('Invalid payload')

    def post(self, url=None, payload=None):
        """'/insert_many', needs list; and '/insert_one', needs tuple.
            insert tuple needs to include proper insert values for table.
            for list, each tuple needs to be same length.
            for autoincrementing value, use None placeholder. """
        if url is None or payload is None:
            raise ValueError('Need valid URL and payload')
        if '/insert' in url:
            if url[-4:] == 'many':
                self.db.insert_many(payload)
                return self.db.commit_change()
            if url[-4:] == '_one':
                self.db.insert_one(payload)
                return self.db.commit_change()
        if url == '/update':
            # payload should be col_id, col_info, index, row_id
            # need to do injection check on raw strings passed as SQL
            if len(payload) == 4:
                self.inj_check(payload[0])
                self.inj_check(payload[2])
                self.db.update_item(payload[0],payload[1],payload[2],payload[3])
                return self.db.commit_change()
            else:
                raise ValueError('Invalid payload length for update method')

    def inj_check(self, input_, string_in=True):
        if string_in:
            if not isinstance(input_, str):
                raise ValueError('Invalid non-string payload')
            if ';' in input_ or 'DROP' in input_:
                raise ValueError('Invalid payload - looks like injection attempt')
            if 'TRUNCATE' in input_ or self.table_name in input_:
                raise ValueError('Invalid payload - looks like injection attempt')


app_ = Front_api('ex_inventory.db','tools')

app_.db.close()
