# LLM Report Generator - Content Restriction Implementation

## Summary
The LLM report generator has been updated to restrict content to only information available from the World Health Organization (WHO) official website (https://www.who.int/). Any requests for information outside WHO sources will be politely declined.

## Files Updated

### 1. `llm_report_generator.py` ⭐ **PRIMARY FILE**
   **Location**: `/Users/hillarykipruto/Documents/Personal2/Trainings/Generative AI for Work/Assignment/llm_report_generator.py`
   
   **Changes Made**:
   - ✅ Updated `_get_system_prompt()` method:
     - Added critical content restriction notice
     - Added language-specific polite decline messages (English, French, Portuguese, Spanish)
     - Enforced WHO-only content policy
     - Added instructions to reference WHO sources
   
   - ✅ Updated `_build_prompt()` method:
     - Added prominent content restriction header at the start of prompts
     - Added validation for custom requirements
     - Added reminders to only use WHO sources
     - Added instructions to decline non-WHO requests politely
   
   **Key Features**:
   - Content restriction enforced at system prompt level
   - Language-specific decline messages for all 4 supported languages
   - Clear instructions to reference WHO sources when appropriate
   - Validation of custom requirements against WHO content availability

### 2. `website.py` ⭐ **SECONDARY FILE**
   **Location**: `/Users/hillarykipruto/Documents/Personal2/Trainings/Generative AI for Work/Assignment/website.py`
   
   **Changes Made**:
   - ✅ Added warning notice on Reports page:
     - Informs users about content restriction
     - Explains that only WHO website content is used
     - Sets expectations for report generation
   
   **Line Updated**: ~1588 (in `render_reports_page()` function)

## Implementation Details

### Content Restriction Mechanism

1. **System Prompt Level**:
   - The system prompt explicitly states that ONLY WHO website content can be used
   - Provides language-specific decline messages
   - Instructs the LLM to reference WHO sources

2. **User Prompt Level**:
   - Prominent header warning about content restriction
   - Validation of custom requirements
   - Reminders throughout the prompt to use only WHO sources

3. **User Interface**:
   - Warning message displayed on Reports page
   - Sets clear expectations for users

### Decline Messages by Language

- **English**: "I apologize, but I can only provide information based on content available from the World Health Organization (WHO) website at https://www.who.int/. For information outside of WHO's official content, please refer to the WHO website directly or consult other authorized sources."

- **French**: "Je m'excuse, mais je ne peux fournir des informations que sur la base du contenu disponible sur le site Web de l'Organisation mondiale de la Santé (OMS) à https://www.who.int/. Pour des informations en dehors du contenu officiel de l'OMS, veuillez consulter directement le site Web de l'OMS ou d'autres sources autorisées."

- **Portuguese**: "Peço desculpas, mas só posso fornecer informações com base no conteúdo disponível no site da Organização Mundial da Saúde (OMS) em https://www.who.int/. Para informações fora do conteúdo oficial da OMS, consulte diretamente o site da OMS ou outras fontes autorizadas."

- **Spanish**: "Me disculpo, pero solo puedo proporcionar información basada en el contenido disponible del sitio web de la Organización Mundial de la Salud (OMS) en https://www.who.int/. Para información fuera del contenido oficial de la OMS, consulte directamente el sitio web de la OMS u otras fuentes autorizadas."

## Testing Recommendations

1. **Test WHO Content Requests**:
   - Request reports on maternal mortality, child mortality, TB
   - Verify reports reference WHO data appropriately

2. **Test Non-WHO Content Requests**:
   - Request information not available on WHO website
   - Verify polite decline messages appear
   - Test in all 4 languages

3. **Test Custom Requirements**:
   - Submit custom prompts with WHO-only topics
   - Submit custom prompts with non-WHO topics
   - Verify appropriate handling of each

## References

- WHO Official Website: https://www.who.int/
- WHO Health Topics: https://www.who.int/health-topics
- WHO Data Hub: https://www.who.int/data

## Notes

- The restriction is enforced at the LLM prompt level
- The LLM is instructed to decline politely, not refuse rudely
- Users are informed upfront about the restriction
- All decline messages are professional and helpful

