import streamlit as st
import time
import re

def stream_response(response_stream, typing_speed: float = 0.25):
    """Stream the response with typewriter effect and formatting"""
    full_response = ""
    message_placeholder = st.empty()
    
    try:
        with st.spinner("Teaching Assistant is typing..."):
            for chunk in response_stream:
                # Check if chunk is an error message (string)
                if isinstance(chunk, str):
                    return chunk
                
                # Get the text from the chunk
                if hasattr(chunk, 'text'):
                    chunk_text = chunk.text
                else:
                    chunk_text = chunk.parts[0].text  # For newer versions of Gemini API
                
                full_response += chunk_text
                
                # Format the response with code blocks and math equations
                formatted_response = format_code_blocks(full_response)
                formatted_response = format_math_equations(formatted_response)
                
                # Add typewriter effect
                message_placeholder.markdown(formatted_response + "▌")
                time.sleep(typing_speed)
        
        message_placeholder.markdown(formatted_response)
        return full_response
        
    except Exception as e:
        error_message = f"An error occurred during streaming: {str(e)}"
        st.error(error_message)
        return error_message

def format_code_blocks(text: str) -> str:
    """Format code blocks with syntax highlighting"""
    
    # Replace ``` code blocks with proper markdown
    pattern = r"```(\w+)?\n(.*?)```"
    
    def replace_code_block(match):
        language = match.group(1) or ""
        code = match.group(2)
        return f"```{language}\n{code}```"
    
    formatted_text = re.sub(pattern, replace_code_block, text, flags=re.DOTALL)
    return formatted_text

def format_math_equations(text: str) -> str:
    """Format mathematical equations"""
    
    # Replace inline math expressions ($...$) with proper LaTeX
    text = re.sub(r'\$(.+?)\$', r'\$\1\$', text)
    
    # Replace block math expressions ($$...$$) with proper LaTeX
    text = re.sub(r'\$\$(.*?)\$\$', r'\$$\1\$$', text, flags=re.DOTALL)
    
    return text