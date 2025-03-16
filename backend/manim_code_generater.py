import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def generate_code(prompt):
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }
    
    response = model.generate_content(
        f""" Create Python code using the Manim library to generate a short educational video about the following topic:
    {prompt}
    
    Analyze and interpret the input:

    Determine the core elements that need to be animated to create an effective visual representation of the concepts provided in the input.
    Break down the information into small, manageable parts for easier conversion into animations.

    Generate Manim code for the animation that follows these standards:

    - Use the Manim library to write code that defines each scene, the graphical elements, and their transformations. The overall animation should 
    explain and visualize the concepts of the content that the user has inputted, which is at the end of this prompt.
    For this video, generate 2-3 examples that comprehensively visualize and explain the concepts which the user wishes to learn.
    All of the Manim code has to be in Python with proper syntax with no errors at all.
    Do not include Markdown Code Block Syntax, using straight raw code only. Do not include "" or "```python" in any location.
    DO NOT EXPLAIN YOUR CODE GENERATION. STRICTLY PROVIDE CODE AND CODE ONLY.
    - You must use MathTex/Tex to write out all text content for proper LaTeX rendering.

    Optimize the Manim code for accessibility and comprehension:

    - Follow a consistent hierarchical structure: main heading at top, subtopics below, and explanatory content should generated below the title.
    - For chemistry and physics content: Ensure chemical formulas, equations, and reaction mechanisms are precisely rendered with proper alignment, 
      subscripts, and superscripts using MathTex. For complex chemical structures, use specialized techniques like VGroup to create molecular diagrams.
    - For mathematical equations in physics: Use the align environment in LaTeX for multi-line equations to ensure proper alignment of equals signs.
    - Never place text at screen edges. Maintain consistent margins (at least 1 unit from any edge of the screen).
    - Implement consistent spacing between text elements (minimum 0.3-0.5 units vertical separation).
    - Use different font sizes appropriately: Titles (1.2-1.5x), subtitles(below the title) (1-1.2x), and body text (below title and subtitle) (standard size).
    - ALWAYS clear the screen completely using self.clear() before introducing new topics or when the screen becomes crowded.
    - Push the title to the top of the screen and the body text to the below of title to maintain a clear visual hierarchy.
    - When introducing new topics, always use a dedicated title screen to signal the transition.
    - For complex reactions or equations, build them step-by-step rather than showing everything at once.
    - The text must make efficient use of screen space with proper line breaks for long equations or expressions.
    - Code must use color strategically for visual separation and highlighting key concepts (maintain WCAG 2.0 AA contrast standards).
    - Create smooth transitions between animations (use transform, FadeIn/FadeOut with appropriate timing).

    Technical Requirements:
    
    - All chemical formulas and equations must use proper LaTeX notation (subscripts, superscripts, charges, etc.)
    - For complex visual elements (atoms, molecules, vectors), use appropriate Manim objects and position them carefully.
    - Ensure objects don't move unexpectedly between animations unless it's part of an intentional transition.
    - Control animation timing to allow viewers to comprehend complex topics (longer wait times for complex equations).
    - Use self.wait() with appropriate durations between animations to allow comprehension.
    - For multi-stage processes, use step-by-step animations that build on previous content.
    - Add descriptive labels to all graphs, diagrams, and visual elements.
    - Check that all objects are properly positioned within the visible area before and after each animation.
    
    As a reminder, your goal is to enable the efficient creation of high-quality animations that help students, educators, and lifelong learners grasp
    complex concepts through visually appealing, easy-to-understand representations.
    If you create a graph of any frame (which is preferred), make sure you CLEAR the frame before and after the render of the entire graph and all its
    components.
    Remember to ALWAYS clear the screen when introducing new major topics. Make sure ALL NEW CONTENT IS ON NEW LINES with proper vertical spacing. 
    NO OVERLAPPING ELEMENTS ARE PERMITTED. Videos should have substantial educational content with proper pacing.
    For especially long equations, break them across multiple lines using LaTeX's alignment environments.
    
    summary:
    1. Use Manim to create clear, engaging educational animations with proper scientific notation
    2. Be complete and ready to run (import all necessary libraries)
    3. Strictly Structure content hierarchically: 
        At most top of video : title
        if the title is generated at centre..then move it to top
        next to title: explanations ( generated below the title line by line with proper spacing from up to down without overlap with title nor overlap between them)
        clear the title if needed (recommended to prevent overlapping)
        clear the title if you feel like screen gonna get filled 
        elements should not go out of video frame and 1 unit margin from all sides
        explanation should be generated below title with proper spacing between them and don't go out of frame
    Clear the screen when you gonna use graphs and make sure entire graph is inside the frame and the graph animations dont overlap with existing elements
    4. Create a scene class named RequestGeneration that inherits from Scene
    5. Use MathTex/Tex for all text to ensure proper chemical and mathematical notation
    6. Clear the screen before new topics and when it becomes crowded
    7. Ensure proper spacing between elements and maintain screen margins
    8. Should have 'Generated by Vision Solve AI' at the end of the video
    Tips: for safer side clear the screen as many times as you can to prevent overlapping elements
    
    Return ONLY the Python code without any explanations, markdown formatting, or code blocks.
    Do not include ```python at the start or ``` at the end.""",
        generation_config=generation_config
    )
    
    return clean_code_response(response.text)

def validate_code(code, language):
    validation_prompt = f"""
    Review the following Manim Python code for errors and optimization opportunities:

    {code}

    As a Manim code validator, focus on these critical aspects:

    1. SYNTAX VALIDATION:
    - Ensure proper Python syntax with no errors
    - Check that all required imports are present (manim, numpy, etc.)
    - Verify class inheritance from Scene and proper method definitions
    - verify if all the varibales are defined and used properly

    2. MANIM-SPECIFIC VALIDATION:
    - Confirm all animation methods are correctly used (play, wait, etc.)
    - Verify mathematical objects are properly created (MathTex, Tex, etc.)
    - Ensure all object transformations maintain object integrity

    3. VISUAL PRESENTATION:
   - Ensure all text and equations are properly positioned on screen with adequate margins
   - Check for overlapping elements that could cause visual confusion

    4. EDUCATIONAL EFFECTIVENESS:
    - Ensure proper pacing for educational comprehension
    - Check that text/equations don't exceed screen boundaries

    5. SPECIFIC FIXES:
    - Replace any instances of 'axes.add_coordinate_labels()' with 'axes.add_coordinates()'
    - Ensure all Unicode characters are properly handled in the code

    6.LATEX VALIDATION:
    - Add 'r' prefix to all LaTeX strings if missing (e.g., MathTex(r"formula") not MathTex("formula"))
    - Ensure all LaTeX expressions are valid syntax
    - Check for balanced braces, brackets, and parentheses in LaTeX code
    - Ensure proper escaping of special characters in LaTeX
    - Replace any Unicode math symbols with proper LaTeX commands
    - Fix empty LaTeX expressions by adding a placeholder like "\\;"

    7.Look out for Value Errors

    8. If you feel like there overlapping add clear screens and also make sure title and explanation dont overlap nor explanation is too bottom

    - IMPORTANT: Never use font_size parameter with the next_to() method - it's not a valid parameter. Instead, set font_size when creating Text or MathTex objects.

   


    if there is no change return the code as it is

    I repeat your top priority is to make sure the code is error free and no overlapping elements and proper Structure content hierarchically: titles at top, explanations are generated below the title from top to bottom!.

    Return ONLY the corrected and optimized code without any explanations, markdown formatting, or code blocks.
    Do not include ```python at the start or ``` at the end.
    """
    
    response = model.generate_content(validation_prompt)
    return clean_code_response(response.text)

def clean_code_response(text):
    text = re.sub(r'^```\w*\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    
    text = re.sub(r'^```[\w]*\n(.*?)\n```$', r'\1', text, flags=re.DOTALL)
    
    return text

def generate_narration_script(prompt):
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 4096,
    }
    
    response = model.generate_content(
        f"""Create a BRIEF narration script for an educational video about:
        
        {prompt}
        
        Your task is to write a concise overview script (about 40-45 seconds when read aloud) that will serve as 
        a voiceover introducing and explaining the key aspects of the topic.
        
        Guidelines:
        1. KEEP IT CONCISE - about 4-6 sentences TOTAL
        2. Focus on introducing the core concept and 2-3 key points
        3. Use simple conversational language suitable for narration
        4. End with an educational conclusion, NOT with "thanks for watching" or similar phrases
        
        IMPORTANT: 
        - The script should be about 80-100 words TOTAL
        - Provide a clear, informative overview of the topic
        - Do NOT include any closing phrases like "thank you", "thanks for watching", etc.
        - Every sentence should provide educational content only
        
        Format the script as plain text with paragraph breaks. Do not include any timestamps, markers, or technical directions.
        Return ONLY the narration script without any explanations or additional formatting.
        """,
        generation_config=generation_config
    )
    
    return clean_code_response(response.text)

def generate_synced_narration(manim_code, prompt):
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 4096,
    }
    
    animation_timings = analyze_animation_timings(manim_code)
    
    response = model.generate_content(
        f"""Create a BRIEF narration script for this Manim animation code about {prompt}:
        
        ```python
        {manim_code}
        ```
        
        Your task is to create a concise narration script with 4-5 sync points for the entire video.
        
        Guidelines:
        1. Include 4-5 sync points TOTAL for the ENTIRE video
        2. Place the sync points at major transitions in the content (title, key sections, conclusion)
        3. Include [SYNC: X] markers at the beginning of each paragraph, where X is the timestamp in seconds
        4. Make each narration segment BRIEF - about 2-3 short sentences per sync point
        5. Total narration should be about 40-45 seconds when read aloud
        6. End with an educational conclusion, NOT with "thanks for watching" or similar phrases
        
        SPECIFICATIONS:
        - 4-5 sync points for the entire video
        - 2-3 short sentences per sync point
        - About 20-25 words per sync point
        - Total word count 80-100 words for the entire script
        - NO closing phrases like "thank you for watching" or similar non-educational content
        
        Format your response as plain text with paragraphs separated by blank lines, including only 4-5 [SYNC: X] markers total.
        Return ONLY the narration script without any other explanations or formatting.
        """,
        generation_config=generation_config
    )
    
    narration_text = clean_code_response(response.text)
    narration_text = remove_closing_phrases(narration_text)
    
    return narration_text

def remove_closing_phrases(text):
    closing_patterns = [
        r'\b(?:thanks|thank\s+you)(?:\s+for\s+(?:watching|listening))?\b',
        r'\bsee\s+you\s+(?:next\s+time|soon)\b',
        r'\bhope\s+you\s+enjoyed\b',
        r'\bgood\s+(?:bye|day|night)\b',
        r'\buntil\s+next\s+time\b'
    ]
    
    for pattern in closing_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def analyze_animation_timings(manim_code):
    timings = []
    current_time = 0
    
    wait_pattern = re.compile(r'self\.wait\(([^)]+)\)')
    for match in wait_pattern.finditer(manim_code):
        try:
            duration = eval(match.group(1))
            if isinstance(duration, (int, float)) and duration > 0:
                current_time += duration
                timings.append({
                    'time': current_time,
                    'type': 'wait',
                    'duration': duration
                })
        except:
            current_time += 1
            timings.append({
                'time': current_time,
                'type': 'wait',
                'duration': 1
            })
    
    play_pattern = re.compile(r'self\.play\(([^)]+)(?:,\s*run_time=([^,)]+))?[^)]*\)')
    for match in play_pattern.finditer(manim_code):
        animation = match.group(1)
        run_time_str = match.group(2)
        
        try:
            if run_time_str:
                run_time = eval(run_time_str)
            else:
                run_time = 1  
                
            if isinstance(run_time, (int, float)) and run_time > 0:
                current_time += run_time
                timings.append({
                    'time': current_time,
                    'type': 'play',
                    'animation': animation[:30] + '...' if len(animation) > 30 else animation,
                    'duration': run_time
                })
        except:
            current_time += 1
            timings.append({
                'time': current_time,
                'type': 'play',
                'animation': animation[:30] + '...' if len(animation) > 30 else animation,
                'duration': 1
            })
    
    return timings

def format_animation_timings(timings):
    result = []
    for t in timings:
        if t['type'] == 'wait':
            result.append(f"Timestamp {t['time']:.1f}s: Pause for {t['duration']:.1f} seconds")
        else:
            result.append(f"Timestamp {t['time']:.1f}s: Animation ({t['animation']})")
    
    return "\n".join(result[:20])  

def generate_and_validate(prompt, language="python", with_audio=False, sync_narration=False):
    print(f"Generating {language} code for: {prompt}")
    
    generated_code = generate_code(prompt)
    print("\n--- Generated Code ---")
    print(generated_code)
    
    narration_script = None
    if with_audio:
        if sync_narration:
            print("\nGenerating synchronized narration script...")
            narration_script = generate_synced_narration(generated_code, prompt)
        else:
            print("\nGenerating narration script...")
            narration_script = generate_narration_script(prompt)
            
        print("\n--- Narration Script ---")
        print(narration_script)
    
    print("\nValidating code...")
    validation_result = validate_code(generated_code, language)
    
    validation_result = clean_code_response(validation_result)
    
    if "No errors found" in validation_result:
        print("✅ No errors found in the generated code.")
        return (generated_code, narration_script) if with_audio else generated_code
    else:
        print("⚠️ Errors found in the generated code.")
        print("\n--- Corrected Code ---")
        print(validation_result)
        
        if with_audio and sync_narration:
            print("\nRegenerating synchronized narration with corrected code...")
            narration_script = generate_synced_narration(validation_result, prompt)
            print("\n--- Updated Narration Script ---")
            print(narration_script)
            
        return (validation_result, narration_script) if with_audio else validation_result

if __name__ == "__main__":
    prompt = input("Enter your code generation prompt: ")
    language = input("Enter the programming language (default: python): ") or "python"
    with_audio = input("Do you want to generate a narration script? (yes/no): ").strip().lower() == "yes"
    
    if with_audio:
        sync_narration = input("Do you want the narration to be synchronized with the animation? (yes/no): ").strip().lower() == "yes"
        generate_and_validate(prompt, language, with_audio=with_audio, sync_narration=sync_narration)
    else:
        generate_and_validate(prompt, language, with_audio=False)
