
# Style Corpus Builder

This document explains **how to teach the framework to sound like a specific AE**
without hardcoding personal details into the Framework layer.

Framework = portable rules  
sample-data = personal style + profile

---

## 1. Where Personal Style Lives

All AE-specific style should live under:

```text
sample-data/Runtime/_Shared/profile/ae_profile.md
sample-data/Runtime/_Shared/style/email_style_corpus__{identifier}.md