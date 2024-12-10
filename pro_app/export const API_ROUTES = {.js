export const API_ROUTES = {
    
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        REFRESH_TOKEN: '/auth/refresh',
        USER_PROFILE: '/auth/profile',        // GET current user's profile
        UPDATE_PROFILE: '/auth/profile/update',  // PUT update current user's profile
    },
    USERS: {
        LIST: '/users',           // GET all users
        CREATE: '/users/create',   // POST create a user
        UPDATE: (id) => `/users/${id}/update`,  // PUT update a user by ID
        DELETE: (id) => `/users/${id}/delete`,  // DELETE a user by ID
    },
    TEAMS: {
        LIST: '/teams',
        CREATE: '/teams/create',
        UPDATE: (id) => `/teams/${id}/update`,
        DELETE: (id) => `/teams/${id}/delete`,
    },
    CLIENTS: {
        LIST: '/clients',
        CREATE: '/clients/create',
        UPDATE: (id) => `/clients/${id}/update`,
        DELETE: (id) => `/clients/${id}/delete`,
    },
    CALENDAR: {
        LIST: '/calendar/events',
        CREATE: '/calendar/events/create',
        UPDATE: (id) => `/calendar/events/${id}/update`,
        DELETE: (id) => `/calendar/events/${id}/delete`,
    },
    MEETINGS: {
        LIST: '/meetings',
        CREATE: '/meetings/create',
        UPDATE: (id) => `/meetings/${id}/update`,
        DELETE: (id) => `/meetings/${id}/delete`,
    },
    TASKS: {
        LIST: '/tasks',
        CREATE: '/tasks/create',
        UPDATE: (id) => `/tasks/${id}/update`,
        DELETE: (id) => `/tasks/${id}/delete`,
    }
};

1. pending forgot password route

yemani510 = y1111 //marketing manager
user 1 = y3333  //marketng director
user 2 = y4444  //marketing assistant
user 3 = y5555  //content writer
user 4 = y6666 //graphics designer
user 5 = y7777  //marketing manager
user 6 = y8888  //graphics designer
user 7 = y9999  //content writer
user 8 = y1111  //content writer
user 9 = y0000  //account manager
user 10 = y1010 //graphics designer
user 11 = y11 11    //marketing manger
user 13 = y1212 //marketing manager
user 14 = y1313 //accountant
user 15 = y1414 //account manager

// set password 
{
    "username": "yemani510",
    "password": "y2222"
}
{
    "username": "lataj60480",
    "password": "y3333"
}
{
    "username": "dijen25422",
    "password": "y7777"
}
lataj60480

// client form data format
{
    "business_name": "ABC Corp",
    "contact_person": "John Doe",
    "business_details": "A company specializing in innovative solutions.",
    "brand_key_points": "Innovation, Customer Service, Reliability",
    "business_address": "123 Main St, Springfield, IL",
    "brand_guidelines_link": "https://example.com/brand-guidelines",
    "business_whatsapp_number": "+1234567890",
    "goals_objectives": "Increase market share and customer retention",
    "business_email_address": "contact@abccorp.com",
    "target_region": "North America",
    "brand_guidelines_notes": "Follow brand colors and tone strictly.",
    "business_offerings": "services + products",  # or "services", "products", "other"
    "list_down_field": "Customized services, technology integration",
    "ugc_drive_link": "https://drive.google.com/drive/folders/example",
    "business_website": "https://www.abccorp.com",
    "social_handles": {
        "facebook": "https://www.facebook.com/abccorp",
        "instagram": "https://www.instagram.com/abccorp",
        "other": [
            "https://www.linkedin.com/company/abccorp",
            "https://twitter.com/abccorp"
        ]
    },
    "additional_notes": "Ensure timely delivery of social media posts."
}


// webdevdata 
{
    "client": 1, 
    "website_type": "ecommerce",  
    "num_of_products": 50, 
    "membership": "yes", 
    "website_structure": "Homepage, About Us, Contact Us, Products",
    "design_preference": "Minimalistic and clean design with a blue color palette",
    "domain": "yes", 
    "domain_info": "example.com",  
    "hosting": "yes", 
    "hosting_info": "Hostgator with unlimited bandwidth",  
    "graphic_assets": "yes",  
    "is_regular_update": "yes",  
    "is_self_update": "no", 
    "additional_notes": "We will require regular SEO updates on the blog section."
  }
  

// CALENDER DATA 
  {
    "date": "2024-09-20",
    "post_count": 1,
    "type": "post",
    "category": "Marketing",
    "cta": "Click here to learn more!",
    "resource": "https://example.com/resource",
    "tagline": "Best Post of the Year",
    "caption": "This is an amazing caption that will grab attention!",
    "hashtags": "#Marketing, #SMM, #BusinessGrowth",
    "creatives": "https://example.com/creatives.png",
    "eng_hooks": "What are your thoughts on this?",
    
    //Internal_Status expectes data
    {
        "internal_status": {
            "content_approval": true,
            "creatives_approval": false
        }
    }
    
    {
        "client_approval": {
            "content_approval": true,
            "creatives_approval": false
        }
    }
    "comments": "The client liked the creative.",
    "collaboration": "Working with Team A to get more insights."
}

{
    "id": 1,
    "calendar": 3,
    "created_at": "2024-10-09T19:00:00Z",
    "date": "2024-10-15",
    "post_count": 5,
    "type": "reel",
    "category": "fitness",
    "cta": "Click here to view more",
    "strategy": "Our strategy focuses on engaging fitness enthusiasts through educational reels.",
    "resource": "https://resource-link.com",
    "tagline": "Stay Fit, Stay Strong",
    "caption": "Daily workout tips to stay fit",
    "hashtags": "#fitness, #workout, #health",
    "creatives": "https://creatives-link.com",
    "e_hooks": "What keeps you motivated to workout?",
    "content_approve_by_marketing_manager": true,
    "content_approve_by_account_manager": true,
    "creatives_approve_by_marketing_manager": false,
    "creatives_approve_by_account_manager": false,
    "internal_status": "pending",
    "client_approval": false,
    "comments": "Need more colorful creatives",
    "collaboration": "Collaborate with influencer X"
}

//MEETING json
{
    "date": "2024-11-01",
    "time": "14:30:00",
    "meeting_name": "Marketing Strategy Session",
    "meeting_link": "https://example.com/meeting-link",
    "timezone": "America/New_York",
    "client": 3,  // Client ID (replace with actual client ID)
    "assignee_type": "team"  // Can be "team" or "marketing_manager" based on who is assigned
}




// #CLIENT INVOICE SUBMISSION 
{
    "billing_from": "2024-10-01",
    "billing_to": "2024-10-31",
    "invoice_status": "unpaid",
    "invoice": "<file.pdf>"
}


//  TEAM CREATION 
{
    "team": {
        "name": "team A",
        "description": "for data operations"
    },
    "members": [
        {"user_id": 30},
        {"user_id": 34},
        {"user_id": 36},
        {"user_id": 39}
    ]
}


// PLAN CREATION 
{
    "plan_name": "Advanced Social Media Plan B",
    "standard_attributes": {
        "stickers": 450, 
        "images": 500, 
        "videos": 450, 
        "reels": 500
    },
    "standard_plan_inclusion": "Basic posting with 4 posts per week.",
    "standard_netprice": 400,
    "advanced_attributes": {
        "stickers": 450, 
        "images": 500, 
        "videos": 450, 
        "reels": 500
    },
    "advanced_plan_inclusion": "Premium posting with 6 posts per week and additional creative services.",
    "advanced_netprice": 600
}

// CLIENT PLAN 
{
    "plan_type": "Advanced",
    "attributes": {
        "reels": 5,
        "posts": 10
    },
    "platforms": {
        "facebook": 100,
        "instagram": 150
    },
    "add_ons": {
        "video_editing": 50,
        "graphics_design": 30
    },
    "grand_total": 600
}

// TO CREATE NOTES
{
 
}

// TO CREATE PLAN STRATEGY
{
    "client": 1,
    "title": "New Strategy",
    "content": "<h1>Q1 Goals</h1><p>Boost engagement by 30%.</p>"
}


agency name, account manager name

//NEW JSON FORMAT FOR CLIENT CREATION
{
    "team": 1,  // Team ID (ForeignKey)
    "account_manager": 2,  // Account Manager ID (ForeignKey)
    "business_name": "ABC Corp",
    "contact_person": "John Doe",
    "business_details": "A leading company in innovative solutions.",
    "brand_key_points": "Innovation, Customer Satisfaction, Quality",
    "business_address": "1234 Elm Street, Springfield",
    "brand_guidelines_link": "https://example.com/brand-guidelines",
    "business_whatsapp_number": "+1234567890",
    "goals_objectives": "Increase market share by 15% this year.",
    "business_email_address": "contact@abccorp.com",
    "target_region": "North America",
    "brand_guidelines_notes": "Ensure all marketing materials follow the brand color scheme.",
    "business_offerings": "services",  // Options: services, products, services_products, other
    "ugc_drive_link": "https://drive.google.com/abc-ugc",
    "business_website": "https://www.abccorp.com",
    "social_handles_facebook": "https://facebook.com/abccorp",
    "social_handles_instagram": "https://instagram.com/abccorp",
    "social_handles_other": [
      {
        "platform": "Twitter",
        "link": "https://twitter.com/abccorp"
      },
      {
        "platform": "LinkedIn",
        "link": "https://linkedin.com/company/abccorp"
      }
    ],
    "additional_notes": "Focus on green initiatives in the upcoming campaign.",
    "proposal_pdf": null,  // Proposal PDF file (optional, can be uploaded separately)
    "proposal_approval_status": "approved",  // Options: approved, declined, changes_required
    "website_type": "ecommerce",  // Options: ecommerce, services
    "num_of_products": 200,  // Only required for ecommerce
    "membership": "yes",  // Options: yes, no
    "website_structure": "A user-friendly, scalable structure.",
    "design_preference": "Minimalistic design with green and blue accents.",
    "domain": "yes",  // Options: yes, no
    "domain_info": "Domain is already purchased: www.abccorp.com",
    "hosting": "yes",  // Options: yes, no
    "hosting_info": "Hosting is managed by AWS.",
    "graphic_assets": "yes",  // Options: yes, no
    "is_regular_update": "yes",  // Options: yes, no
    "is_self_update": "no",  // Options: yes, no
    "additional_webdev_notes": "Integrate with the existing CRM for seamless operations."
  }
  