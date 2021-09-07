FROM timothyantonius/explain_python

WORKDIR /explain

CMD ["jupyter", "lab", "--port=8880", "--no-browser", "--ip=0.0.0.0", "--allow-root"]