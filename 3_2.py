from pymongo import MongoClient


try:
    test_value = int(input("Введите сумму: "))

    client = MongoClient('localhost', 27017)

    db = client['test_db']
    collection = db.vacancies

    res = db.collection.find({"$or": [{"salary_min": {"$gt": test_value}}, {"salary_max": {"$gt": test_value}}]})

    print(*list(res), sep='\n')

except ValueError:
    print('Ввели не число')
