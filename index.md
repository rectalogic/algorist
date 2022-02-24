---
title: Algorist
---

# Algorist

{% assign renders = site.static_files | where: "render", true %}
{% for render in renders %}
  <img src="{{ site.baseurl }}{{ render.path }}" />
{% endfor %}

