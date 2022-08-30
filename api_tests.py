from front_api import Front_api
import unittest


class Api_test(unittest.TestCase):
    def test_book_get(self):
        test_app = Front_api('ex_inventory.db','books')
        test_slice = test_app.get()[:3]
        expected = [('October Revolution', 'Y Geronovsky', 'history'),
                    ('American Wetlands', 'Mary Chandler', 'geography'),
                    ('Monstrous Appetite', 'Mark Appleton', 'horror')]
        self.assertListEqual(test_slice,expected)

    def test_book_get_where(self):
        test_app = Front_api('ex_inventory.db','books')
        test_quer = test_app.get('/where',['genre','technical'])
        expected = [('Glazier Manual', 'BC Thompson', 'technical'),
                    ('Timber Framing & Construction', 'Richard Clark', 'technical'),
                    ('The Handy Gardener', 'Susan Bower', 'technical')]
        self.assertListEqual(test_quer,expected)

    def test_book_get_where_err(self):
        test_app = Front_api('ex_inventory.db', 'books')
        with self.assertRaises(ValueError) as err:
            test_app.get('/where', )
        self.assertEqual(str(err.exception),'Invalid payload - needs to be at least 2 items')

    def test_book_get_where_inj_err(self):
        test_app = Front_api('ex_inventory.db', 'books')
        with self.assertRaises(ValueError) as err:
            test_app.get('/where', ('genre = fiction;) DROP TABLE books;','blank'))
        self.assertEqual(str(err.exception),'Invalid payload - looks like injection attempt')

    def test_book_post_insert(self):
        test_app = Front_api('ex_inventory.db','books')
        test_app.post('/insert_one',('The Biscay and Breton Coast','Anton Beauchard','geography'))
        test_quer = test_app.get('/where', ['genre', 'geography'])
        expected = ('The Biscay and Breton Coast','Anton Beauchard','geography')
        self.assertEqual(test_quer[-1],expected)

    def test_book_post_update(self):
        test_app = Front_api('ex_inventory.db','books')
        test_app.post('/update', ('title','Les Cotes Gasconnes et Bretonnes', 'author', 'Anton Beauchard'))
        test_quer = test_app.get('/where',['genre','geography'])
        expected = ('Les Cotes Gasconnes et Bretonnes','Anton Beauchard','geography')
        self.assertEqual(test_quer[-1],expected)

    def test_books_clean_up(self):
        test_app = Front_api('ex_inventory.db','books')
        test_app.db.delete_item('author','Anton Beauchard')
        test_app.db.commit_change()
        test_quer = test_app.get('/where',['genre','geography'])
        expected = ('American Highlands', 'Mary Chandler', 'geography')
        self.assertEqual(test_quer[-1], expected)

    def test_tools_get_where_gte(self):
        test_app = Front_api('ex_inventory.db','tools')
        test_quer = test_app.get('/where',['price',200.00,'>='])
        expected = [(1, 'table saw', 'Makita', 267.49, 4),(15, 'combo welder', 'Miller', 2400.35, 7),
                    (16, 'welding hood', 'Esab', 333.99, 12),(18, 'plasma cutter', 'Lincoln', 1119.68, 2)]
        self.assertListEqual(test_quer,expected)

    def test_tools_get_where_lte(self):
        test_app = Front_api('ex_inventory.db','tools')
        test_quer = test_app.get('/where',['price',28.00,'<='])
        expected = [(5, 'garden shears', 'Fiskars', 24.39, 4),(8, 'brick trowel', 'Marshalltown', 26.43, 4),
                    (11, '1 lb plastic mallet', 'ABC', 19.23, 6),
                    (12, '15-piece brass and steel punch set', 'Wheeler', 27.99, 6),
                    (13, 'carpenter hammer', 'Craftsman', 13.98, 18)]
        self.assertListEqual(test_quer,expected)

    def test_tools_get_where_fine_lte(self):
        test_app = Front_api('ex_inventory.db', 'tools')
        test_quer = test_app.get('/where',['price', 28.00,('id','type','count'),'<=',True])
        expected = [(13, 'carpenter hammer', 18), (11, '1 lb plastic mallet', 6), (5, 'garden shears', 4),
                    (8, 'brick trowel', 4), (12, '15-piece brass and steel punch set', 6)]
        self.assertListEqual(test_quer, expected)

    def test_machines_batch_ins(self):
        test_app = Front_api('ex_inventory.db', 'machines')
        mach_list = [('ride on lawn mower', 'John Deere', 1995.43), ('ride on lawn mower', 'Husqvarna', 2399.90),
                     ('chainsaw', 'Husqvarna', 396.78), ('chainsaw', 'Ryobi', 182.05)]
        test_app.post('/insert_many',mach_list)
        test_quer = test_app.get()
        self.assertListEqual(test_quer[-4:],mach_list)

    def test_machines_clean_up(self):
        test_app = Front_api('ex_inventory.db', 'machines')
        test_app.db.delete_item('name','ride on lawn mower')
        test_app.db.delete_item('name','chainsaw')
        test_app.db.commit_change()
        test_quer = test_app.get()
        expected = [('CNC mill', 'Langmuir', 4495),('CNC router', 'Shark', 4999),
                    ('angle grinder', 'Black & Decker', 45),('angle grinder', 'Dewalt', 90)]
        self.assertListEqual(test_quer[-4:],expected)


if __name__ == "__main__":
    unittest.main()
