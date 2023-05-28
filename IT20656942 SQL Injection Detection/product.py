import injectionfree as inj


is_it_sql = inj.predict_sqlinjection("SELECT * FROM users WHERE id = 1 OR 1=1")

if is_it_sql:
    print("It's SQL Injection!")
else:
    print("It's not SQL Injection!")