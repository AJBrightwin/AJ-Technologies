from django.db import models



class contactform(models.Model):

    username = models.CharField(max_length=100)

    mobile_number = models.CharField(max_length=15)

    email = models.EmailField(max_length=254)

    message = models.TextField(max_length=2000)

   



    def __str__(self):

        return self.username

   



class homeproject(models.Model):

    project_name = models.CharField(max_length=100)

    project_photo = models.ImageField(upload_to='project_photo/', blank=True, null=True)

    project_Title = models.CharField(max_length=100)

    project_description = models.TextField(max_length=2000)

    project_tag = models.CharField(max_length=40)

    project_link = models.URLField(max_length=200, blank=True, null=True)

   

   



    def __str__(self):

        return self.project_name



class portfolioproject(models.Model):

    portfolio_image = models.ImageField(upload_to='portfolio_photo/', blank=True, null=True)

    portfolio_Title = models.CharField(max_length=100)

    portfolio_description = models.TextField(max_length=2000)

    portfolio_tag = models.CharField(max_length=40)

    portfolio_link = models.URLField(max_length=200, blank=True, null=True)

   

   



    def __str__(self):

        return self.portfolio_Title    


class testimonial(models.Model):

    client_name = models.CharField(max_length=100)

    client_testimonial = models.TextField(max_length=2000)

    client_company = models.CharField(max_length=100)

    def __str__(self):

        return self.client_name

    @property
    def client_initial(self):

        return self.client_name[:1].upper() if self.client_name else ''