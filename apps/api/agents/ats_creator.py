import dspy
import json
import os
from pydantic import BaseModel
from typing import List

# --- 1. Configuration (from your code) ---
# Make sure to replace "YOUR_GEMINI_API_KEY" or load it from a .env file
# from config.config import settings
# lm = dspy.LM("google/gemini-1.5-flash", api_key=settings.GEMINI_API_KEY)

# For demonstration purposes, let's configure it directly
try:
    api_key = os.environ["GEMINI_API_KEY"]
except KeyError:
    print("Please set the GEMINI_API_KEY environment variable.")
    exit()

lm = dspy.LM("gemini/gemini-2.5-flash", api_key=api_key)
dspy.configure(lm=lm)


# --- 2. Define the DSPy Signature ---
# This translates our prompt's requirements into a programmable structure for DSPy.
class ATSSignature(dspy.Signature):
    """Analyze the React component source code and extract its Abstract Technical Specification (ATS) into structured fields."""

    # --- Input Field ---
    component_code = dspy.InputField(
        desc="The full source code of the React/TypeScript component."
    )

    # --- Output Fields (each key of our JSON) ---
    componentName = dspy.OutputField(
        desc="The exact exported name of the React component (e.g., 'Button')."
    )
    description = dspy.OutputField(
        desc="A concise, one-sentence summary of the component's primary function."
    )
    dependencies = dspy.OutputField(
        desc='A JSON-formatted list of all external package names imported (e.g., ["react", "@radix-ui/react-slot"]).'
    )
    internalDependencies = dspy.OutputField(
        desc='A JSON-formatted list of all internal, alias-based imports (e.g., ["@/lib/utils"]).'
    )
    propsInterface = dspy.OutputField(
        desc="A JSON-formatted object detailing each prop. For each prop, include its type, if it's optional, and a list of options if defined in a cva function."
    )
    tags = dspy.OutputField(
        desc='A JSON-formatted list of 3-5 relevant, lowercase keywords (e.g., ["button", "ui", "interaction"]).'
    )
    rawCode = dspy.OutputField(
        desc="The complete, unmodified source code from the input, formatted as a single JSON string."
    )


# --- 3. Define Pydantic Models for a Validated Output ---
# This ensures the AI's string output is converted into a clean, validated object.
class PropDetail(BaseModel):
    type: str
    isOptional: bool
    options: List[str] | None


class ATSModel(BaseModel):
    componentName: str
    description: str
    dependencies: List[str]
    internalDependencies: List[str]
    propsInterface: dict[str, PropDetail]
    tags: List[str]
    rawCode: str


# --- 4. The ATSCreator Class ---
class ATSCreator:
    def __init__(self):
        # The predictor is a simple dspy.Module that uses our signature.
        self.predictor = dspy.Predict(ATSSignature)

    def create_ats_from_file(self, file_path: str) -> ATSModel | None:
        """
        Reads a component file, generates its ATS, and validates the output.
        """
        # 1. Get component file
        try:
            with open(file_path, "r") as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None

        # 2. Pass it to the dspy agent (predictor)
        prediction = self.predictor(component_code=code)

        # 3. Get the output and parse it
        try:
            # Combine the string outputs into a single JSON-like structure
            # DSPy outputs each field as a string, so we need to construct a valid JSON string
            # and then parse it.

            # Since propsInterface and dependencies are complex, we ask the LLM
            # to format them as JSON strings directly in the signature.

            # Pre-process the props to align with the Pydantic model
            props_interface_raw = json.loads(prediction.propsInterface)
            processed_props = {}
            for prop_name, prop_details in props_interface_raw.items():
                processed_props[prop_name] = {
                    "type": prop_details.get("type"),
                    "isOptional": prop_details.get("optional", False),
                    "options": prop_details.get("options"),
                }

            output_dict = {
                "componentName": prediction.componentName,
                "description": prediction.description,
                "dependencies": json.loads(prediction.dependencies),
                "internalDependencies": json.loads(prediction.internalDependencies),
                "propsInterface": processed_props,
                "tags": json.loads(prediction.tags),
                "rawCode": prediction.rawCode,
            }

            # Validate the dictionary with our Pydantic model
            validated_ats = ATSModel(**output_dict)
            return validated_ats
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error parsing or validating the AI's output: {e}")
            print("--- Raw Prediction ---")
            print(prediction)
            return None
