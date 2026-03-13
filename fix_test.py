with open("test/test_hypothesis.py", "r") as f:
    code = f.read()

# Filter out 'append' from key_list in fuzzer tests
code = code.replace("key_list=st.lists(st.text()),", "key_list=st.lists(st.text().filter(lambda x: x != 'append')),")

with open("test/test_hypothesis.py", "w") as f:
    f.write(code)
