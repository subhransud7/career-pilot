from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def analyze(self, raw_text: str) -> dict:
        """
        Analyze the raw_text and return a dict with fields:
        {role, experience, seniority, location, company, recruiter, recruiter_profile_link, email, score}
        """
        raise NotImplementedError
