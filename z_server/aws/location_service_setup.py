"""
AWS locatoin services



Walk through with maps

https://dev.to/sigitp/introduction-to-amazon-location-service-part1-62a

We are going to use Amazon Cognito for user access control. In this example, we will use Unauthenticated Identities from Cognito Identity Pools for simple lab purposes only, in real-life application, you want to use Authenticated Identities so that only authenticated users can use your map. Always follow Best practices for Amazon Location Service.


Amazon cognito power user access added to engdevlab

If you have a website with anonymous users, you may want to use API Keys or Amazon Cognito.



wt_webservices_user
- s3 full access
- location full access
- 

HERE MAPS!
https://www.here.com/learn/blog/build-and-deploy-location-apps-with-aws-location-services-and-here
but also Amplify Geo??



. At present, five types of functions are available: map display function, address search function, route search function, geofence function, and tracking function. This time, I added the address search function and built a map application!


configure:
 Amazon Location Place indexes in the AWS console.

Click "Place indexes".


Amplify to build geo app

cognito 1 hour access etc
https://dev.to/mepa1363/how-to-build-an-online-route-planner-with-amazon-location-service-pn0



https://awspolicygen.s3.amazonaws.com/policygen.html

for ARN apply to all:
    arn:aws:geo:*:*:*


    {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1696764002498",
      "Action": "geo:*",
      "Effect": "Allow",
      "Resource": "arn:aws:geo:*:*:*"
    }
  ]
}


 to Amazon Cognito and receive temporary, scoped-down credentials that are valid for an hour.


watchtowerbucket


??????
add amazon location service to amplify map view
https://dev.to/aws-builders/building-an-address-lookup-function-with-amazon-location-service-3fdm

https://www.here.com/learn/blog/build-and-deploy-location-apps-with-aws-location-services-and-here

https://dev.to/aws-builders/building-an-address-lookup-function-with-amazon-location-service-3fdm


For each service used, Amplify creates a CloudFormation template and the parameters necessary to create the service. Writing CloudFormation templates can be complex, but Amplify generates them base on the choices you make when prompted and your user credentials.


"""