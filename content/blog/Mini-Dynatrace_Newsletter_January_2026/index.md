---
title: Mini Dynatrace Newsletter - January 2026 Edition
subtitle: Document Management with Admin Rights, Segment Filters for Anomaly Detectors & Removing Outdated (Custom) Metrics with the API
description: Document Management with Admin Rights, Segment Filters for Anomaly Detectors & Removing Outdated (Custom) Metrics with the API
authors: [Marina Pollehn]
date: '2026-01-31'
tags: [Observability, Dynatrace, Releasenotes, Newsletter]
draft: false
---
As already mentioned in my very first newsletter, 
I will try to share and highlight new relevant Dynatrace
features (mostly from the Dynatrace release notes)
more frequently - seasoned with my personal
opinions, ideas and practical context.
And of course, there is much to share again from the 
past 2 months - meaning I should also be quick with another February newsletter to catch up.
---------------------------------------------------------------------------------------------------------------------------------------------

## Settings - Management of dashboards, notebooks, and other documents for administrators

__When?__ available since 18 nov 2025, SaaS version 1.328
(auto-update, so if you have SaaS this feature is available automatically)
__Summary (from the release notes):__ "A new Document Management page has been
introduced in Settings, giving administrators enhanced
control over organizational documents.
The Document Management page enables administrators to:
- View all documents (dashboards, notebooks, and other document types)
across the environment.
- Manage document ownership and sharing permissions.
- Access comprehensive document listings for all users.
To access the Document Management page, users must have the
document:documents:admin permission scope. This scope has
been automatically added to the predefined Admin User policy.
With this permission scope, you can now utilize the admin-access
flag on all document API operations. 
This will bypass any ownership or sharing access controls,
and you can manage all documents in this environment to change sharing,
ownership, or download content.
When opening documents directly from the management view:
Documents can only be opened if you have existing access permissions independent of your admin privileges and to view documents without direct access (for example, a dashboard owned by another user), you must first do one of the following:
- Transfer ownership to yourself.
- Add a sharing permission for yourself.
- This workflow can be optimized, and additional improvements
will be included in future updates."

__Details:__ To find the Document Management page, you need to go to Settings > General
__My 2cts:__ Okay, I was waiting for this for so long, so I am definitely positive!
I was pretty much spamming the Dyantrace community with the wish of finally having a decent overview of all dashboards as an admin - also in the UI 
(that was also something we all were used to on Dynatrace Managed). 
Do I love the new feature? Yes. Do I think it's easy to find? No. 
I think other former Dynatrace Managed users will agree, 
that finding this as an additional admin tab in the
regular Dashboards or Notebooks app, would feel more natural.
I would definitely move it there, for more intuitive navigation.
Then again, we often saw features move in SaaS, like the OpenPipeline 
app which became a Setting, so maybe it will also happen the other way around.
What would I like to see next? For me, group ownership is a must.
Right now, every document can only have one owner - a specific person or service user (please don't randomly assign a group via the API, this seems to create
problems which you can only solve with admin rights:
[Dynatrace Community - Dashboard ownership changed to group losing the share and delete rights](https://community.dynatrace.com/t5/Dashboarding/Dashboard-ownership-changed-to-group-losing-the-share-and-delete/m-p/277561#M5090)).
What's the issue with a group of users not being
allowed as the owners? Imagine I share a
dashboard with my teammembers, but me and them
are not admins. Then they will not be able to share the dashboard with
others while I am on leave - even if I gave them edit rights. Another benefit is that
no one will have to claim my dashboard if my account is deleted, for example
due to leaving the company. Did I convince you
that group ownership of documents is needed? Then you can upvote my idea here:
[Dynatrace Community - Assign a Dashboard owner for a team](https://community.dynatrace.com/t5/Product-ideas/Assign-a-Dashboard-owner-for-a-team/idc-p/275164#M55805)


## Davis - Filtering by segments for Anomaly Detection

__When?__ since 16 dec 2025, SaaS version 1.329
(auto-update, so if you have SaaS this feature is
available automatically)
__Summary (from the release notes):__ "Anomaly Detection now supports
filtering by segments, allowing you to narrow alerts to,
for example, specific applications, regions, or Kubernetes clusters.
You can apply segments directly within an alert widget to create
context-aware alerting configurations.
Segments configured in the Notebooks or Dashboards app are
automatically inherited by the alert widget, 
maintaining context as you switch from data exploration to alert creation.
When you navigate from Anomaly Detection to Notebooks or Dashboards via Open with, selected segments are automatically applied."
__Details:__

__My 2cts:__ I would probably use this feature mainly to apply Teams or App segment filters. For different teams managing anomaly detectors, using the segments will give a better view of their own configured alerts/forecasts, and hence their scope of responsibility. I do love the inherit functionalities that were released with this feature.

## Platform - New API for easier removal of outdated custom metrics

__When?__ since 16 dec 2025, SaaS version 1.329
(auto-update, so if you have SaaS this feature is
available automatically)
__Summary (from the release notes):__ "The environment API now
provides a new endpoint to bulk delete custom metrics that 
haven’t been written in a given number of days:
`DELETE /api/v2/metrics?metricSelector=<your-selector>&minUnusedDays=<nr-of-days>`
Use the `metricSelector` parameter to select metrics to be deleted. You can use wildcards to delete:
Metrics that match a prefix.
- All metrics (by selecting *).
- Use the `minUnusedDays` parameter to specify at which point matching metrics should be deleted.
For example, `minUnusedDays=60` will delete all matching metrics that haven’t been written in the last 60 days."
__Details:__

__My 2cts:__ I never really saw this feature aa must. Technically, I don't
see much of a reason to delete "old" custom metrics,
even though I was asked by customers before to do it.
Usually, these metrics served a purpose, also making them relevant
when looking at old data.
Sometimes people are bothered by an "old" metric showing up in the Metrics app.
This app has the timeframe selector functionality, 
meaning by selecting a more recent one, you will no longer see the "old" metrics.
Other people are bothered by the old metrics still showing 
up on their dashboards - the thing with that is,
that you will still have to remove the old tiles
referencing the old metrics anyways - even if they
already don't exist anymore.
So the only good reason, in my opinion, are the costs. You don't pay
for querying metrics and the costs for the ingest are
sunk costs which cannot be recovered. But you do pay the costs
of retaining metrics. 
If you pay the list price, 

---------------------------------------------------------------------------------------------------------------------------------------------

If this is your first time reading my newsletters,
you have probably now hit the point where you start
thinking: Okay, why would I call this a mini newsletter?
I mean, this was quite a long article...?
This was only a sub-set of all the new features published in the last weeks.
In the release notes, you can find even more features,
but mostly with only a few details and little description.
With these types of newsletters, I am trying to give these improvements
and adjustments a bit of practical context and give
everyone a chance to test them as soon as possible.
