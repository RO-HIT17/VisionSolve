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
    8. Should have 'Generated by Exam Buddy' at the end of the video
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

def generate_and_validate(prompt, language="python"):
    print(f"Generating {language} code for: {prompt}")
    
    generated_code = generate_code(prompt)
    print("\n--- Generated Code ---")
    print(generated_code)
    
    print("\nValidating code...")
    validation_result = validate_code(generated_code, language)
    
    validation_result = clean_code_response(validation_result)
    
    if "No errors found" in validation_result:
        print("✅ No errors found in the generated code.")
        return generated_code
    else:
        print("⚠️ Errors found in the generated code.")
        print("\n--- Corrected Code ---")
        print(validation_result)
        return validation_result

if __name__ == "__main__":
    prompt = input("Enter your code generation prompt: ")
    language = input("Enter the programming language (default: python): ") or "python"
    generate_and_validate(prompt, language)
