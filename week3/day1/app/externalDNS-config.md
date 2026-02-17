
With external DNS provider additional steps are needed .
After creating load balancer  it has created 2 additional public IP on Elastic IP
Check them and verify they are registered in public DNS:

<img width="657" height="178" alt="image" src="https://github.com/user-attachments/assets/15ed5352-cbe8-46b3-ba8f-8b861c6028bb" />

Creating the A name in AWS pointing to the ALB:

<img width="661" height="265" alt="image" src="https://github.com/user-attachments/assets/e4b5152a-1400-4358-bf84-ec68b2a137e8" />


I need to create a CNAME record in external DNS with subdomain week3 where I registered my domain and point to the AWS load balancer


<img width="899" height="138" alt="image" src="https://github.com/user-attachments/assets/c22e85c5-edb0-4617-8838-5d6a8727807a" />



For HTTPS I requested certificate from Amazon Certificate manager :


<img width="890" height="157" alt="image" src="https://github.com/user-attachments/assets/ef92dae7-0408-4799-a738-3e591dad139e" />




If you’re using external DNS service no need to create a CNAME record in ROUTE 53: 

First you need to add CAA record in DNS in order to allow Amazon to validate the certificate.
Below the servers for Certificate Manager: 

amazon.com  
amazontrust.com  
awstrust.com  
amazonaws.com

<img width="900" height="175" alt="image" src="https://github.com/user-attachments/assets/2b33ed8d-cec7-4cdf-8b61-f7380ffbb5a7" />


To have certificate validates need to create a CNAME record in DNS Provider:

<img width="855" height="208" alt="image" src="https://github.com/user-attachments/assets/684ab122-cb41-4f2b-8255-4017a9de6392" />


and finally is “Issued”:

	![Uploading image.png…]()





