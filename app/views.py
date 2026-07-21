import json
import re
import os
from django.shortcuts import render

# Try importing new google.genai package first, with fallback to legacy google.generativeai
USE_NEW_GENAI = False
GENAI_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
    USE_NEW_GENAI = True
except ImportError:
    try:
        import google.generativeai as genai_legacy
        GENAI_AVAILABLE = True
        USE_NEW_GENAI = False
    except ImportError:
        GENAI_AVAILABLE = False

# Try importing TextBlob for local fallback sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False


def local_sentiment_analysis(raw_text):
    """
    Fallback local NLP sentiment analyzer when Gemini API is unavailable or fails.
    """
    # Split text into non-empty comment lines or sentences
    raw_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    # If comments are separated by bullet points or commas instead of linebreaks
    comments = []
    for line in raw_lines:
        # Strip bullet points or numbers (e.g., "1. Good product" -> "Good product")
        cleaned_line = re.sub(r'^\d+[\.\)]\s*|^[\-\*\•]\s*', '', line).strip()
        if cleaned_line:
            comments.append(cleaned_line)

    if not comments:
        comments = [raw_text.strip()]

    positive_count = 0
    negative_count = 0
    neutral_count = 0
    comment_details = []
    suggestions = []

    suggestion_keywords = ['suggest', 'recommend', 'should', 'could', 'please', 'add', 'feature', 'fix', 'improve', 'wish', 'need', 'instead', 'better if']

    for comment in comments:
        # Check sentiment using TextBlob if available, otherwise keyword heuristic
        if TEXTBLOB_AVAILABLE:
            analysis = TextBlob(comment)
            polarity = analysis.sentiment.polarity
            if polarity > 0.1:
                sentiment = 'positive'
                reason = f"Positive tone (score: {polarity:.2f})"
                positive_count += 1
            elif polarity < -0.1:
                sentiment = 'negative'
                reason = f"Negative tone (score: {polarity:.2f})"
                negative_count += 1
            else:
                sentiment = 'neutral'
                reason = "Neutral tone"
                neutral_count += 1
        else:
            # Simple keyword polarity fallback
            pos_words = {'good', 'great', 'awesome', 'excellent', 'love', 'best', 'like', 'amazing', 'nice', 'helpful', 'fast', 'superb', 'happy', 'cool', 'perfect'}
            neg_words = {'bad', 'worst', 'terrible', 'horrible', 'slow', 'hate', 'bug', 'crash', 'issue', 'poor', 'useless', 'broken', 'error', 'fail', 'disappointed'}
            words = set(re.findall(r'\w+', comment.lower()))
            pos_matches = words.intersection(pos_words)
            neg_matches = words.intersection(neg_words)

            if len(pos_matches) > len(neg_matches):
                sentiment = 'positive'
                reason = f"Positive keywords: {', '.join(pos_matches)}"
                positive_count += 1
            elif len(neg_matches) > len(pos_matches):
                sentiment = 'negative'
                reason = f"Negative keywords: {', '.join(neg_matches)}"
                negative_count += 1
            else:
                sentiment = 'neutral'
                reason = "Neutral feedback"
                neutral_count += 1

        # Extract potential suggestions
        if any(kw in comment.lower() for kw in suggestion_keywords):
            suggestions.append(comment)

        comment_details.append({
            'text': comment,
            'sentiment': sentiment,
            'reason': reason
        })

    total = len(comments)
    advice_text = " • ".join(suggestions) if suggestions else "No explicit recommendations detected in the comments."

    return {
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'total_count': total,
        'advice': advice_text,
        'comment_details': comment_details,
        'source': 'Local NLP Engine'
    }


def analyze_with_gemini(raw_text):
    """
    Analyzes sentiment using Google Gemini API returning clean structured data.
    """
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set. "
        "Please configure it before running the application."
    )
    
    prompt = f"""You are a professional sentiment analysis system. Analyze the following user comments:
\"\"\"{raw_text}\"\"\"

Return ONLY valid JSON matching this structure:
{{
  "positive_count": <number of positive comments>,
  "negative_count": <number of negative/bad feedback comments>,
  "neutral_count": <number of neutral comments>,
  "total_count": <total number of comments>,
  "advice": "<summary of recommendations, advice, or feature requests suggested by users>",
  "comment_details": [
    {{
      "text": "<comment text>",
      "sentiment": "positive" | "negative" | "neutral",
      "reason": "<brief 1-sentence reason>"
    }}
  ]
}}"""

    models_to_try = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]
    last_error = None

    if USE_NEW_GENAI:
        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            temperature=0.2,
            top_p=0.95,
            max_output_tokens=2048,
            response_mime_type="application/json",
        )

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                response_text = response.text.strip()

                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    data['source'] = f'Gemini AI ({model_name})'
                    return data
            except Exception as err:
                last_error = err
                continue
    else:
        genai_legacy.configure(api_key=api_key)
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "max_output_tokens": 2048,
            "response_mime_type": "application/json",
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        for model_name in models_to_try:
            try:
                model = genai_legacy.GenerativeModel(
                    model_name=model_name,
                    safety_settings=safety_settings,
                    generation_config=generation_config,
                )
                response = model.generate_content(prompt)
                response_text = response.text.strip()

                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    data['source'] = f'Gemini AI ({model_name})'
                    return data
            except Exception as err:
                last_error = err
                continue

    raise last_error or ValueError("Failed to reach Gemini models")


def index(request):
    if request.method == 'POST':
        creation_input = request.POST.get('creationInput', '').strip()

        if not creation_input:
            return render(request, 'app/home.html', {
                'error': 'Please enter comments before submitting for analysis.',
                'creation_input': creation_input
            })

        result_data = None
        error_msg = None

        # Primary attempt: Gemini AI Analysis
        if GENAI_AVAILABLE:
            try:
                result_data = analyze_with_gemini(creation_input)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "Quota exceeded" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    error_msg = "Note: Gemini API rate limit or quota reached. Analysis provided via local NLP engine."
                elif "404" in err_str or "NotFound" in err_str:
                    error_msg = "Note: Gemini model unavailable. Analysis provided via local NLP engine."
                else:
                    error_msg = f"Note: Gemini API notice ({e}). Analysis provided via local NLP engine."

        # Fallback: Local NLP Engine
        if not result_data:
            try:
                result_data = local_sentiment_analysis(creation_input)
            except Exception as fallback_err:
                return render(request, 'app/home.html', {
                    'error': f"An error occurred while analyzing comments: {fallback_err}",
                    'creation_input': creation_input
                })

        pos = result_data.get('positive_count', 0)
        neg = result_data.get('negative_count', 0)
        neu = result_data.get('neutral_count', 0)
        tot = result_data.get('total_count', 0) or (pos + neg + neu) or 1

        pos_pct = round((pos / tot) * 100, 1)
        neg_pct = round((neg / tot) * 100, 1)
        neu_pct = round((neu / tot) * 100, 1)

        context = {
            'creation_input': creation_input,
            'positive_comments': pos,
            'negative_comments': neg,
            'neutral_comments': neu,
            'total': tot,
            'pos_pct': pos_pct,
            'neg_pct': neg_pct,
            'neu_pct': neu_pct,
            'advice': result_data.get('advice', 'No specific advice found.'),
            'comment_details': result_data.get('comment_details', []),
            'analysis_source': result_data.get('source', 'AI System'),
            'api_notice': error_msg
        }

        return render(request, 'app/home.html', context)

    # GET request
    return render(request, 'app/home.html')