---
title: Algorist
---

# Algorist

{% assign renders = site.static_files | where: "render", true %}
{% for render in renders %}
  {% assign name = render.name | split: "." %}
  <a href="https://github.com/rectalogic/algorist/tree/master/examples/{{ name[0] }}.py"><img src="{{ site.baseurl }}{{ render.path }}" /></a>
{% endfor %}

