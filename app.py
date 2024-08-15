import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import openai
import requests
from io import BytesIO

# GPT API 키 입력
st.title("DALL·E 3 기반 포스터 만들기")
api_key = st.text_input("OpenAI API 키를 입력하세요:", type="password")

# 텍스트 입력
prompt = st.text_input("이미지를 생성할 텍스트를 입력하세요:")

# 이미지 생성 및 표시
if st.button("이미지 생성"):
    if api_key and prompt:
        openai.api_key = api_key

        # DALL·E 3 API 호출
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size='1024x1024'
        )

        image_url = response['data'][0]['url']

        # 이미지 가져오기 및 변환
        image_response = requests.get(image_url)
        img_pil = Image.open(BytesIO(image_response.content))
        st.image(img_pil, caption="Generated Image", use_column_width=True)

        # 이미지를 그리기 위한 배경 이미지로 사용
        st.session_state['bg_image'] = img_pil

# 그림 도구 설정
drawing_mode = st.sidebar.selectbox(
    "Drawing tool:", ("freedraw", "line", "rect", "circle")
)

stroke_width = st.sidebar.slider("글자 크기:", 1, 25, 3)
stroke_color = st.sidebar.color_picker("색깔:", "#000000")
bg_color = st.sidebar.color_picker("배경색 지정:", "#ffffff")
realtime_update = st.sidebar.checkbox("실시간 반영", True)

# 캔버스 컴포넌트 생성
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # 고정된 채우기 색상 및 투명도
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    background_image=st.session_state['bg_image'] if 'bg_image' in st.session_state else None,
    update_streamlit=realtime_update,
    height=1024,
    width=1024,
    drawing_mode=drawing_mode,
    key="canvas",
)

# 이미지 데이터 및 경로 처리
if canvas_result.image_data is not None:
    # 캔버스에서 얻은 데이터를 RGBA 형식으로 변환
    overlay_image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGB')

    # 배경 이미지와 합성
    if 'bg_image' in st.session_state:
        # 합성하기 위해서 배경 이미지와 오버레이 이미지를 같은 크기로 맞추기
        background_image = st.session_state['bg_image'].copy().convert("RGBA")
        overlay_image = overlay_image.resize(background_image.size).convert("RGBA")

        # 합성 이미지 생성
        combined_image = Image.alpha_composite(background_image, overlay_image)
    else:
        combined_image = overlay_image

    # 합성된 이미지 표시
    st.image(combined_image, caption="Final Image")

    # 이미지를 다운로드할 수 있는 형식으로 변환
    buf = BytesIO()
    combined_image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="이미지 다운로드",
        data=byte_im,
        file_name="final_image.png",
        mime="image/png",
    )

