import streamlit as st

#### Show Simple Streamlit Use cases

st.title('My Test Page')

st.markdown('## This is a markdown header')

if st.button('Say hello'):
    st.write('Hello!')

my_name = st.text_input('Enter your name')
st.write('Your name is:', my_name)

my_number = st.number_input('Enter a number', value=1, min_value=1, max_value=10)
picked_number = st.slider('Pick a number', min_value=0, max_value=int(my_number), step=1)

@st.experimental_dialog("My Dialog",width="large")
def my_dialog():
    st.write('Hello from the dialog!')
    if st.button('Lets do it!'):
        st.success('YES!')
        if st.button('Close'):
            st.rerun()

if picked_number == my_number:
    my_dialog()



