# test_gemini_integration.py
import os

from agents.ats_creator import ATSCreator


def test_gemini_integration():
    # Check if API key is set
    if "GEMINI_API_KEY" not in os.environ:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        print("Please set it with: export GEMINI_API_KEY='your-api-key'")
        return

    # Sample React component code
    test_component = """
    import * as React from "react"
    import { Slot } from "@radix-ui/react-slot"
    import { cva, type VariantProps } from "class-variance-authority"

    const buttonVariants = cva(
        "inline-flex items-center justify-center rounded-md text-sm font-medium",
        {
            variants: {
                variant: {
                    default: "bg-primary text-primary-foreground",
                    destructive: "bg-destructive text-destructive-foreground",
                },
                size: {
                    default: "h-10 px-4",
                    sm: "h-9 px-3",
                },
            },
            defaultVariants: {
                variant: "default",
                size: "default",
            },
        }
    )

    export interface ButtonProps
        extends React.ButtonHTMLAttributes<HTMLButtonElement>,
            VariantProps<typeof buttonVariants> {
        asChild?: boolean
    }

    const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
        ({ className, variant, size, asChild = false, ...props }, ref) => {
            const Comp = asChild ? Slot : "button"
            return (
                <Comp
                    className={cn(buttonVariants({ variant, size, className }))}
                    ref={ref}
                    {...props}
                />
            )
        }
    )
    Button.displayName = "Button"

    export { Button, buttonVariants }
    """

    # Create a temporary file with the test component
    temp_file = "test_button.tsx"
    with open(temp_file, "w") as f:
        f.write(test_component)

    try:
        print("Testing Google Gemini API integration...")
        print("This might take a few seconds...\n")

        # Create ATSCreator instance
        creator = ATSCreator()

        # Test the component analysis
        result = creator.create_ats_from_file(temp_file)

        if result:
            print("✅ Success! Component analysis completed.")
            print("\nAnalysis Results:")
            print(f"Component Name: {result.componentName}")
            print(f"Description: {result.description}")
            print(f"Dependencies: {', '.join(result.dependencies)}")
            print(f"Tags: {', '.join(result.tags)}")
            print("\nProps Interface:")
            for prop_name, prop_details in result.propsInterface.items():
                print(
                    f"  - {prop_name}: {prop_details.type} {'(optional)' if prop_details.isOptional else ''}"
                )
                if prop_details.options:
                    print(f"    Options: {', '.join(prop_details.options)}")
        else:
            print(
                "❌ Failed to analyze the component. Please check the error message above."
            )

    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    test_gemini_integration()
