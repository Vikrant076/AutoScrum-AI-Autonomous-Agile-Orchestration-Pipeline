# test_groq.py
import groq

def test_groq_connection():
    try:
        # Test with a dummy key first to check if library loads
        client = groq.Groq(api_key="dummy-key")
        print("✅ Groq library imported successfully")
        print("✅ Groq client created successfully")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_groq_connection()