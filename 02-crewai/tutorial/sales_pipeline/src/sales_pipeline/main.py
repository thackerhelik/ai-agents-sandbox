#!/usr/bin/env python
from pathlib import Path

from pydantic import BaseModel

from crewai.flow import Flow, listen, start, and_, or_, router

from sales_pipeline.crews.email_engagement.email_engagement import EmailEngagement
from sales_pipeline.crews.lead_qualification.lead_qualification import LeadQualification


class SalesPipeline(Flow):

    @start()
    def fetch_leads(self):
        # Pull our leads from the database
        leads = [
            {
                "lead_data": {
                    "name": "João Moura",
                    "job_title": "Director of Engineering",
                    "company": "Clearbit",
                    "email": "joao@clearbit.com",
                    "use_case": "Using AI Agent to do better data enrichment."
                }
            },
        ]
        return leads

    @listen(fetch_leads)
    def score_leads(self, leads):
        scores = LeadQualification().crew().kickoff_for_each(leads)
        self.state["score_crews_results"] = scores
        return scores
        
    @listen(score_leads)
    def store_leads_score(self, scores):
        # Here we would store the scores in the database
        return scores
    
    @listen(score_leads)
    def filter_leads(self, scores):
        filtered_leads = []
        for output in scores:
            if output.pydantic and output.pydantic.lead_score.score > 70:
                filtered_leads.append(output.pydantic)

        self.state["filtered_leads"] = filtered_leads
        return filtered_leads
    
    @listen(and_(filter_leads, store_leads_score))
    def log_leads(self, *args):
        filtered_leads = self.state.get("filtered_leads", [])
        print(f"Logged {len(filtered_leads)} qualified leads.")

    @router(filter_leads)
    def count_leads(self, scores):
        if len(scores) > 10:
            return "high"
        elif len(scores) > 5:
            return "medium"
        else:
            return "low"
        
    @listen("high")
    def store_in_salesforce(self, leads):
        return leads
    
    @listen("medium")
    def send_to_sales_team(self, leads):
        return leads
    
    @listen("low")
    def write_email(self, leads_string):
        leads_to_email = self.state.get("filtered_leads", [])
        scored_leads = [lead.model_dump() for lead in leads_to_email]

        emails = EmailEngagement().crew().kickoff_for_each(scored_leads)
        return emails
    
    @listen(write_email)
    def send_email(self, emails):
        # Here we should send the emails to the lead
        return emails


def kickoff():
    sales_flow = SalesPipeline()
    final_emails = sales_flow.kickoff()

    print("\n" + "="*50)
    print("📊 PIPELINE METRICS") # & COSTS")
    print("="*50)

    # 1. Calculate Lead Qualification Metrics
    score_results = sales_flow.state.get("score_crews_results", [])
    if score_results:
        # Sum up the tokens across all the leads we processed
        qual_tokens = sum(result.token_usage.total_tokens for result in score_results)
        # qual_cost = 0.150 * (qual_tokens / 1000000)
        print(f"Lead Qualification Tokens: {qual_tokens}")
        # print(f"Lead Qualification Cost:   ${qual_cost:.4f}")

    # 2. Calculate Email Engagement Metrics
    if final_emails and isinstance(final_emails, list):
        email_tokens = sum(result.token_usage.total_tokens for result in final_emails)
        # email_cost = 0.150 * (email_tokens / 1000000)
        print(f"Email Engagement Tokens:   {email_tokens}")
        # print(f"Email Engagement Cost:     ${email_cost:.4f}")

    print("="*50 + "\n")

def plot():
    sales_flow = SalesPipeline()
    
    # Pass the filename directly into the plot method
    sales_flow.plot("screwai_flow.html")
    
    print("\n" + "="*70)
    print("🗺️ FLOWCHART CREATED LOCALLY!")
    print("="*70 + "\n")


def run_with_trigger():
    """
    Run the flow with trigger payload.
    """
    import json
    import sys

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    sales_flow = SalesPipeline()

    try:
        result = sales_flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the flow with trigger: {e}")


if __name__ == "__main__":
    kickoff()
