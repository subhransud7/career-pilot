from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from app.db.models import Lead
from app.agents.router import AgentRouter
from app.services.search import search_linkedin_posts
from app.services.fetch import fetch_post_content


class Aggregator:

    def __init__(self, db: Session):
        self.db = db
        self.router = AgentRouter()

    def already_exists(self, post_link: str):
        return self.db.query(Lead).filter(Lead.post_link == post_link).first()

    def process_post(self, post_link: str):

        if self.already_exists(post_link):
            return None

        raw_text = fetch_post_content(post_link)

        analyze_result, analyze_agent = self.router.run(
            "analyze_post",
            {"post_text": raw_text}
        )

        score_result, score_agent = self.router.run(
            "score_job",
            analyze_result
        )

        email_result, email_agent = self.router.run(
            "generate_email",
            analyze_result
        )

        linkedin_result, linkedin_agent = self.router.run(
            "generate_linkedin_message",
            analyze_result
        )

        lead = Lead(
            post_link=post_link,
            recruiter_profile_link=analyze_result.get("recruiter_profile_link"),
            raw_post=raw_text,
            role=analyze_result.get("role"),
            experience=analyze_result.get("experience"),
            seniority=analyze_result.get("seniority"),
            location=analyze_result.get("location"),
            company=analyze_result.get("company"),
            recruiter=analyze_result.get("recruiter"),
            email=analyze_result.get("email"),
            score=score_result.get("score"),
            score_reason=score_result.get("reason"),
            email_subject=email_result.get("subject"),
            email_body=email_result.get("body"),
            linkedin_message=linkedin_result.get("message"),
            agent_used=f"{analyze_agent}/{score_agent}"
        )

        self.db.add(lead)
        self.db.commit()

        return lead

    def run(self, keywords: str, days: int, max_results: int = 10):

        links = search_linkedin_posts(keywords, days, max_results)

        results = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.process_post, link) for link in links]

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print("Error processing post:", e)

        return results
