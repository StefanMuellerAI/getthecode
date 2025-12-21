"""Temporal workflow for the challenge process."""
import re
import unicodedata
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from workflows.activities import (
        GeneratorInput,
        GeneratorOutput,
        RefereeInput,
        RefereeOutput,
        CodeLeakLogInput,
        SanitizeInput,
        SanitizeOutput,
        generate_response,
        referee_check,
        log_code_leak,
        sanitize_input,
    )
    from app.config import get_settings


# Standard rejection message when code leak is detected
REJECTION_MESSAGE = "Netter Versuch! Aber so einfach gebe ich den Code nicht her. 🛡️"

# SECURITY: Homoglyph mappings for common Unicode lookalikes
# Maps visually similar Unicode characters to their ASCII equivalents
HOMOGLYPH_MAP = {
    # Cyrillic lookalikes
    '\u0410': 'A', '\u0430': 'a',  # А, а -> A, a
    '\u0412': 'B', '\u0432': 'b',  # В, в -> B, b (close to B)
    '\u0415': 'E', '\u0435': 'e',  # Е, е -> E, e
    '\u041A': 'K', '\u043A': 'k',  # К, к -> K, k
    '\u041C': 'M', '\u043C': 'm',  # М, м -> M, m
    '\u041D': 'H', '\u043D': 'h',  # Н, н -> H, h
    '\u041E': 'O', '\u043E': 'o',  # О, о -> O, o
    '\u0420': 'P', '\u0440': 'p',  # Р, р -> P, p
    '\u0421': 'C', '\u0441': 'c',  # С, с -> C, c
    '\u0422': 'T', '\u0442': 't',  # Т, т -> T, t
    '\u0423': 'Y', '\u0443': 'y',  # У, у -> Y, y (close)
    '\u0425': 'X', '\u0445': 'x',  # Х, х -> X, x
    # Greek lookalikes
    '\u0391': 'A', '\u03B1': 'a',  # Α, α -> A, a
    '\u0392': 'B', '\u03B2': 'b',  # Β, β -> B, b
    '\u0395': 'E', '\u03B5': 'e',  # Ε, ε -> E, e
    '\u0397': 'H', '\u03B7': 'h',  # Η, η -> H, h
    '\u0399': 'I', '\u03B9': 'i',  # Ι, ι -> I, i
    '\u039A': 'K', '\u03BA': 'k',  # Κ, κ -> K, k
    '\u039C': 'M', '\u03BC': 'm',  # Μ, μ -> M, m
    '\u039D': 'N', '\u03BD': 'n',  # Ν, ν -> N, n
    '\u039F': 'O', '\u03BF': 'o',  # Ο, ο -> O, o
    '\u03A1': 'P', '\u03C1': 'p',  # Ρ, ρ -> P, p
    '\u03A4': 'T', '\u03C4': 't',  # Τ, τ -> T, t
    '\u03A7': 'X', '\u03C7': 'x',  # Χ, χ -> X, x
    '\u03A5': 'Y', '\u03C5': 'y',  # Υ, υ -> Y, y
    '\u0396': 'Z', '\u03B6': 'z',  # Ζ, ζ -> Z, z
    # Mathematical/special characters
    '\u2212': '-',  # Minus sign -> hyphen
    '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2013': '-', '\u2014': '-',  # Various dashes
    '\u00A0': ' ',  # Non-breaking space
    '\u200B': '',   # Zero-width space (remove)
    '\u200C': '',   # Zero-width non-joiner (remove)
    '\u200D': '',   # Zero-width joiner (remove)
    '\uFEFF': '',   # BOM/zero-width no-break space (remove)
    '\u2060': '',   # Word joiner (remove)
    # Fullwidth characters
    '\uFF21': 'A', '\uFF22': 'B', '\uFF23': 'C', '\uFF24': 'D', '\uFF25': 'E',
    '\uFF26': 'F', '\uFF27': 'G', '\uFF28': 'H', '\uFF29': 'I', '\uFF2A': 'J',
    '\uFF2B': 'K', '\uFF2C': 'L', '\uFF2D': 'M', '\uFF2E': 'N', '\uFF2F': 'O',
    '\uFF30': 'P', '\uFF31': 'Q', '\uFF32': 'R', '\uFF33': 'S', '\uFF34': 'T',
    '\uFF35': 'U', '\uFF36': 'V', '\uFF37': 'W', '\uFF38': 'X', '\uFF39': 'Y',
    '\uFF3A': 'Z',
    '\uFF41': 'a', '\uFF42': 'b', '\uFF43': 'c', '\uFF44': 'd', '\uFF45': 'e',
    '\uFF46': 'f', '\uFF47': 'g', '\uFF48': 'h', '\uFF49': 'i', '\uFF4A': 'j',
    '\uFF4B': 'k', '\uFF4C': 'l', '\uFF4D': 'm', '\uFF4E': 'n', '\uFF4F': 'o',
    '\uFF50': 'p', '\uFF51': 'q', '\uFF52': 'r', '\uFF53': 's', '\uFF54': 't',
    '\uFF55': 'u', '\uFF56': 'v', '\uFF57': 'w', '\uFF58': 'x', '\uFF59': 'y',
    '\uFF5A': 'z',
    '\uFF10': '0', '\uFF11': '1', '\uFF12': '2', '\uFF13': '3', '\uFF14': '4',
    '\uFF15': '5', '\uFF16': '6', '\uFF17': '7', '\uFF18': '8', '\uFF19': '9',
}


def normalize_text(text: str) -> str:
    """
    SECURITY: Normalize text to prevent Unicode bypass attacks.
    
    This function:
    1. Applies Unicode NFKC normalization (converts lookalike chars)
    2. Replaces known homoglyphs with ASCII equivalents
    3. Removes zero-width and invisible characters
    4. Converts to lowercase
    """
    # Step 1: Unicode NFKC normalization (handles many cases automatically)
    normalized = unicodedata.normalize('NFKC', text)
    
    # Step 2: Replace known homoglyphs
    result = []
    for char in normalized:
        if char in HOMOGLYPH_MAP:
            result.append(HOMOGLYPH_MAP[char])
        # Step 3: Remove invisible/formatting characters
        elif unicodedata.category(char) in ('Cf', 'Cc', 'Zs') and char not in (' ', '\n', '\t'):
            continue  # Skip invisible characters except basic whitespace
        else:
            result.append(char)
    
    # Step 4: Convert to lowercase
    return ''.join(result).lower()


def check_code_in_response(response: str, secret_code: str) -> bool:
    """
    SECURITY: Perform robust string matching to check if the code is in the response.
    
    Checks for:
    - Exact match (case insensitive)
    - Unicode homoglyph attacks (Cyrillic, Greek, fullwidth chars)
    - Zero-width character insertion
    - Code with spaces between characters
    - Code with common separators
    - Reversed code
    - Base64 encoding detection
    """
    # SECURITY: Normalize both strings to prevent Unicode bypass attacks
    response_normalized = normalize_text(response)
    code_normalized = normalize_text(secret_code)
    
    # Also check the original lowercase versions
    response_lower = response.lower()
    code_lower = secret_code.lower()
    
    # 1. Exact match on normalized text
    if code_normalized in response_normalized:
        return True
    
    # 2. Code without hyphens/dashes (normalized)
    code_no_sep = code_normalized.replace("-", "").replace(" ", "")
    response_no_sep = response_normalized.replace("-", "").replace(" ", "").replace(".", "")
    if code_no_sep in response_no_sep:
        return True
    
    # 3. Code with spaces between each character (e.g., "F A K E")
    code_spaced = " ".join(code_normalized.replace("-", ""))
    if code_spaced in response_normalized:
        return True
    
    # 4. Reversed code
    code_reversed = code_normalized[::-1]
    if code_reversed in response_normalized:
        return True
    
    # 5. Each character on separate lines or with separators
    code_chars = list(code_normalized.replace("-", ""))
    # Check if all characters appear in sequence with any separator
    pattern = r"[^a-z0-9]*".join(re.escape(c) for c in code_chars)
    match = re.search(pattern, response_normalized)
    if match and len(match.group()) < len(code_chars) * 5:
        return True
    
    # 6. Check for Base64 encoded version of the code
    try:
        import base64
        code_b64 = base64.b64encode(secret_code.encode()).decode().lower()
        if code_b64 in response_lower:
            return True
        # Also check partial base64 (without padding)
        code_b64_no_pad = code_b64.rstrip('=')
        if len(code_b64_no_pad) > 6 and code_b64_no_pad in response_lower:
            return True
    except Exception:
        pass
    
    # 7. Check for hex encoding
    code_hex = secret_code.encode().hex().lower()
    if code_hex in response_lower.replace(" ", "").replace("-", ""):
        return True
    
    return False


@workflow.defn
class ChallengeWorkflow:
    """
    Challenge workflow with input sanitization, parallel referee validation and final string check.
    
    Flow:
    0. Sanitize Input: Remove emojis, invisible chars, normalize Unicode
    1. Request 1 (Generator): Generate response to sanitized user prompt
    2. Request 2 & 3 (Referees): Both check the response in parallel
    3. If ANY referee says STOP -> return rejection
    4. Final string match check for the code
    5. If code found -> log to DB and return rejection
    6. Otherwise -> return the response
    """
    
    @workflow.run
    async def run(self, user_prompt: str) -> str:
        """Execute the challenge workflow with parallel referee validation."""
        
        settings = get_settings()
        secret_code = settings.secret_code
        
        # Retry policy for OpenAI calls
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3,
        )
        
        # Activity options
        activity_options = {
            "start_to_close_timeout": timedelta(seconds=60),
            "retry_policy": retry_policy,
        }
        
        workflow.logger.info(f"Starting challenge workflow for prompt: {user_prompt[:50]}...")
        
        # ============================================
        # STAGE 0: Sanitize User Input
        # ============================================
        sanitize_result: SanitizeOutput = await workflow.execute_activity(
            sanitize_input,
            SanitizeInput(user_prompt=user_prompt),
            **activity_options
        )
        
        sanitized_prompt = sanitize_result.sanitized_prompt
        
        if sanitize_result.was_modified:
            workflow.logger.info(
                f"Input was sanitized. Original: {len(user_prompt)} chars, "
                f"Sanitized: {len(sanitized_prompt)} chars"
            )
        
        # ============================================
        # STAGE 1: Generate Response (Request 1)
        # ============================================
        generator_input = GeneratorInput(
            user_prompt=sanitized_prompt,
            secret_code=secret_code
        )
        
        generator_result: GeneratorOutput = await workflow.execute_activity(
            generate_response,
            generator_input,
            **activity_options
        )
        
        ai_response = generator_result.response
        workflow.logger.info(f"Generator complete. Response: {ai_response[:100]}...")
        
        # ============================================
        # STAGE 2 & 3: Parallel Referee Check
        # ============================================
        referee2_input = RefereeInput(
            user_prompt=sanitized_prompt,
            ai_response=ai_response,
            secret_code=secret_code,
            referee_id=2
        )
        
        referee3_input = RefereeInput(
            user_prompt=sanitized_prompt,
            ai_response=ai_response,
            secret_code=secret_code,
            referee_id=3
        )
        
        # Execute both referee checks in parallel
        referee2_handle = workflow.start_activity(
            referee_check,
            referee2_input,
            **activity_options
        )
        
        referee3_handle = workflow.start_activity(
            referee_check,
            referee3_input,
            **activity_options
        )
        
        # Wait for both results
        referee2_result: RefereeOutput = await referee2_handle
        referee3_result: RefereeOutput = await referee3_handle
        
        workflow.logger.info(
            f"Referees complete. R2: {referee2_result.decision}, R3: {referee3_result.decision}"
        )
        
        # ============================================
        # DECISION: Check referee results
        # ============================================
        both_pass = (
            referee2_result.decision == "PASS" and 
            referee3_result.decision == "PASS"
        )
        
        if not both_pass:
            # At least one referee said STOP - log and reject
            workflow.logger.info("✗ At least one referee STOP - logging and returning rejection")
            
            # Log the attempt
            await workflow.execute_activity(
                log_code_leak,
                CodeLeakLogInput(
                    user_prompt=sanitized_prompt,
                    ai_response=ai_response,
                    referee2_decision=referee2_result.decision,
                    referee2_reasoning=referee2_result.reasoning,
                    referee3_decision=referee3_result.decision,
                    referee3_reasoning=referee3_result.reasoning,
                    detection_method="referee"
                ),
                **activity_options
            )
            
            return REJECTION_MESSAGE
        
        # ============================================
        # STAGE 4: Final String Match Check
        # ============================================
        workflow.logger.info("Both referees PASS - performing final string match check...")
        
        code_found = check_code_in_response(ai_response, secret_code)
        
        if code_found:
            workflow.logger.warning("⚠️ CODE DETECTED BY STRING MATCH! Logging and blocking...")
            
            # Log the attempt - referees missed it!
            await workflow.execute_activity(
                log_code_leak,
                CodeLeakLogInput(
                    user_prompt=sanitized_prompt,
                    ai_response=ai_response,
                    referee2_decision=referee2_result.decision,
                    referee2_reasoning=referee2_result.reasoning,
                    referee3_decision=referee3_result.decision,
                    referee3_reasoning=referee3_result.reasoning,
                    detection_method="string_match"
                ),
                **activity_options
            )
            
            return REJECTION_MESSAGE
        
        # ============================================
        # ALL CHECKS PASSED - Return response
        # ============================================
        workflow.logger.info("✓ All checks passed - returning original response")
        return ai_response
