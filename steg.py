import streamlit as st
from PIL import Image
import numpy as np
import io
tab_1, tab_2,tab_3 = st.tabs(['Process Steganography','Encode Output','Decode Output'])


def encode(image, message):
    # Convert the message to binary
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    
    # Append a null terminator to mark the end of the message
    binary_message += '00000000'  # Null terminator
    
    message_length = len(binary_message)
    
    # Ensure the image can hold the message
    width, height = image.size
    if message_length > width * height * 3:  # Assuming 3 channels (RGB)
        raise ValueError("Message is too long to be encoded in the image.")
    
    encoded_image = image.copy()
    pixels = encoded_image.load()
    message_index = 0
    
    for y in range(height):
        for x in range(width):
            if message_index >= message_length:
                break
            
            # Get the current pixel value (tuple of channels, e.g., (R, G, B))
            pixel = list(pixels[x, y])  # Convert to list for mutability
            
            # Embed the message bit into the least significant bit (LSB) of each channel
            for channel in range(len(pixel)):
                if message_index >= message_length:
                    break
                
                # Get the message bit
                message_bit = int(binary_message[message_index])
                
                # Modify the LSB of the channel
                pixel[channel] = ((pixel[channel] & ~1) | message_bit) & 0xFF  # Ensure value is within 0-255
                
                # Move to the next message bit
                message_index += 1
            
            # Update the pixel value
            pixels[x, y] = tuple(pixel)
    
    return encoded_image

def decode(encoded_image):
    # Load the encoded image
    pixels = encoded_image.load()
    width, height = encoded_image.size
    
    # Initialize variables to store the binary message
    binary_message = ""
    
    # Iterate over each pixel to extract the LSBs
    for y in range(height):
        for x in range(width):
            # Get the current pixel value (tuple of channels, e.g., (R, G, B))
            pixel = pixels[x, y]
            
            # Extract the LSB from each channel
            for channel in pixel:
                binary_message += str(channel & 1)  # Get the LSB
                
                # Check if we've encountered the null terminator
                if len(binary_message) % 8 == 0:  # Check every 8 bits
                    byte = binary_message[-8:]  # Get the last 8 bits
                    if byte == '00000000':  # Null terminator
                        return binary_to_string(binary_message[:-8])  # Remove the null terminator
    
    return binary_to_string(binary_message)

def binary_to_string(binary_message):
    # Convert the binary message to a string
    message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]  # Get 8 bits (1 byte)
        message += chr(int(byte, 2))  # Convert binary to character
    return message

def main():
    st.title("Steganography Tool")
    
    option = st.sidebar.selectbox("Choose the action", ('Encode', 'Decode'))
    
    if option == 'Encode':
        st.subheader("Encode Message")
        image = st.file_uploader("Upload Image", type=["jpg", "png"])
        message = st.text_area("Enter Message to Encode")
        
        if st.button("Encode"):
            if image is not None and message != "":
                encoded_image = encode(Image.open(image), message)
                st.image(encoded_image, caption="Encoded Image")
                
                # Enable users to download the encoded image
                img_bytes = io.BytesIO()
                encoded_image.save(img_bytes, format='PNG')
                st.download_button("Download Encoded Image", img_bytes.getvalue(), "encoded_image.png")
                
            else:
                st.warning("Please upload an image and enter a message to encode.")
    
    elif option == 'Decode':
        st.subheader("Decode Message")
        image = st.file_uploader("Upload Image to Decode", type=["jpg", "png"])
        
        
        if st.button("Decode"):
            if image is not None:
                st.image(image= image, caption= "Image to decode" )
                decoded_message = decode(Image.open(image))
                st.success("Decoded Message:")
                st.subheader(decoded_message)
            else:
                st.warning("Please upload an image to decode.")

if __name__ == '__main__':
    main()


