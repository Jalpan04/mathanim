from app.services.hybrid_router import route_and_generate

test_input = "draw y=4"
result = route_and_generate(test_input)

if result:
    print("MATCHED!")
    print(result[:200])
else:
    print("NO MATCH")
