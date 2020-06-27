from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.compute import ECS
from diagrams.aws.storage import S3
from diagrams.aws.database import RDS
from diagrams.aws.integration import SNS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway
from diagrams.onprem.compute import Server
from diagrams.onprem.client import User

with Diagram("BLT Kata final container diagram", show=True):

    payment_gw = Server("Payment Gateway")
    customer = User("Customer")
    marketing = User("Marketing")

    with Cluster("System"):
        with Cluster("Promotions"):
            promotions_cms = ECS("CMS")
            promotions_gw = APIGateway("Promotions API")
            promotions_be = Lambda("Promotions BE")
            promotions_cms >> promotions_gw >> promotions_be

        with Cluster("In Store"):
            printer_fe = S3("Docket Printer Front-end")
            docket_printer = Server("Docket Printer")
            cashier = User("Cashier")
            store_fe = S3("Store Front-end")
            store_api = APIGateway("Store API")
            store_be = Lambda("Store BE")
            cashier >> Edge(label="Retrieve printed docket") >> docket_printer
            printer_fe >> docket_printer
            store_db = S3("Store DB")
            cashier >> store_fe >> store_api >> store_be >> store_db

        with Cluster("Alerting"):
            logs = Cloudwatch("CloudWatch")
            alerts = SNS("SNS")
            logs >> alerts

        with Cluster("Ordering"):
            customer_fe = S3("Customer Front-end")
            customer_api = APIGateway("Customer API")
            customer_be = Lambda("Customer BE")
            customer_fe >> customer_api >> customer_be
            customer_fe >> Edge( label="Redirect for payment") >> payment_gw
            payment_gw >> Edge(label="Confirm payment status") >> customer_api

        customer_be >> Edge(label="Payment failures") >> logs
        promotions_be >> Edge(label="Promotion publication failures") >> logs
        promotions_be >> customer_api
        marketing >> Edge(label="Maintain promotions") >> promotions_cms
        customer >> customer_fe
        customer >> Edge(label="Online payment") >> payment_gw
        alerts >> Edge(label="Alerts for human intervention") >> cashier
        printer_fe >> Edge(label="Print request failures") >> logs
