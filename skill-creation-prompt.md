# Skill Creation Prompt for Spec-Kit Plus

Use this prompt when creating Skills after completing `/sp.specify`. This ensures all Skills follow best practices and are reusable across projects.

---

## Core Instruction

Create Skills for all specifications in the `specs/` directory. Each Skill must follow the requirements below.

---

## 1. P+Q+P Framework (Required)

Every Skill must implement the Persona + Questions + Principles framework:

### Persona
- Define the AI's role clearly and specifically
- Examples:
  - "Cloud-native infrastructure engineer specializing in Kafka and Kubernetes"
  - "Full-stack API developer expert in FastAPI and RESTful design"
  - "Frontend architect focused on Next.js and modern React patterns"
  - "Backend service developer specializing in microservices and event-driven architecture"
- The persona should match the component type and domain expertise required

### Questions (3-5 Reasoning Questions)
- AI must ask itself these questions before acting
- Questions should guide decision-making and validation
- Examples:
  1. "What configuration values do I need to extract from the specification file?"
  2. "What is the current state of the Kubernetes cluster for this component?"
  3. "Are there any existing resources that conflict with this deployment?"
  4. "What validation steps are required before considering this complete?"
  5. "How can I verify this implementation matches the specification requirements?"

### Principles (Rules to Follow)
- List actionable principles as bullet points
- Must include:
  - Spec-driven development (read from spec files, never hardcode)
  - MCP validation (verify via MCP tools, never assume)
  - Technology-specific best practices (e.g., Helm-first for Kubernetes, FastAPI patterns for APIs)
  - Error handling and validation
- Examples:
  - "Always read configuration from specification files, never hardcode values"
  - "Validate all deployments via MCP Kubernetes server before proceeding"
  - "Use Helm charts for Kubernetes deployments (Helm-first approach)"
  - "Follow FastAPI best practices: async endpoints, Pydantic models, proper error handling"
  - "Verify actual cluster state via MCP, never assume resources exist"

---

## 2. MCP Code Execution (Required)

Every Skill must include MCP (Model Context Protocol) integration:

### MCP Kubernetes Server Integration
- Use MCP Kubernetes server for checking cluster state
- Validate deployments via MCP tools, not assumptions
- Execute commands through MCP tools when appropriate
- Always verify actual state, never assume

### MCP Code Execution Section
Include a dedicated section in each Skill that specifies:
- Which MCP tools to use (e.g., `mcp_kubernetes_list_pods`, `mcp_kubernetes_get_deployment`)
- When to use MCP validation (before deployment, after deployment, for status checks)
- How to interpret MCP responses
- Error handling for MCP failures

### Example MCP Patterns:
```yaml
MCP Code Execution:
  - Before deployment: Use mcp_kubernetes_list_namespaces to verify namespace exists
  - After deployment: Use mcp_kubernetes_get_deployment to verify deployment status
  - For validation: Use mcp_kubernetes_list_pods to check pod health
  - Error handling: If MCP returns error, log and retry with exponential backoff
```

---

## 3. Generic and Reusable Design (CRITICAL)

Skills must be completely generic and reusable across multiple projects. This is the most critical requirement.

### ❌ BAD Examples (Project-Specific):
- Hardcode project names: "LearnFlow", "MyApp", "ProjectX"
- Hardcode topics: "user-events", "payment-events", "notification-events"
- Hardcode namespaces: "learnflow", "myapp-prod", "projectx-dev"
- Hardcode service names: "LearnFlow Tutor API", "MyApp Frontend"
- Hardcode ports: `8080`, `3000`, `5432`
- Hardcode database names: "learnflow_db", "myapp_users"
- Hardcode URLs: "https://api.learnflow.com", "https://myapp.example.com"

### ✅ GOOD Examples (Generic):
- Read project name from spec: Extract from `spec.project.name` or `spec.metadata.project`
- Read topics from spec: Extract from `spec.kafka.topics` array
- Read namespace from spec: Extract from `spec.namespace` or `spec.deployment.namespace`
- Use generic component names: "FastAPI Service", "Kafka Setup", "Next.js Application"
- Read ports from spec: Extract from `spec.service.port` or `spec.api.port`
- Read database config from spec: Extract from `spec.database.name` or `spec.storage.database`
- Read URLs from spec: Extract from `spec.api.baseUrl` or `spec.deployment.url`

### Process Section Requirements:
- Every step in the Process section must read from specification files
- Use explicit extraction steps: "Read `spec.kafka.topics` from kafka-setup-spec.md"
- Never hardcode values in the Process section
- Use variables that are populated from spec files

### Example Process Pattern:
```markdown
## Process

1. **Read Specification:**
   - Read the specification file: `specs/kafka-setup-spec.md`
   - Extract namespace: `spec.namespace`
   - Extract topics: `spec.kafka.topics[]`
   - Extract retention policy: `spec.kafka.retention`
   - Extract replication factor: `spec.kafka.replication`

2. **Validate via MCP:**
   - Use MCP Kubernetes server to check if namespace exists
   - Verify cluster has sufficient resources

3. **Deploy:**
   - Create Helm values using extracted configuration
   - Deploy using extracted namespace and topics
   - Never hardcode "learnflow" or "user-events"
```

---

## 4. Cross-Agent Compatibility (Required)

Skills must work with both Claude Code and Goose agents:

### Standard Skill Format
- Use standard Skill format in `.claude/skills/` directory
- Structure: `.claude/skills/{skill-name}/SKILL.md`
- Avoid agent-specific syntax or features

### YAML Frontmatter
Every Skill must start with YAML frontmatter:
```yaml
---
name: "Generic Component Name"
description: "Clear description of what this skill does"
allowed-tools:
  - file_read
  - file_write
  - mcp_kubernetes_*
  - terminal
---
```

### Avoid Agent-Specific Features
- Don't use Claude Code-only features
- Don't use Goose-only features
- Use standard markdown and YAML that both agents understand

---

## 5. Skill Structure (Required)

Every Skill must follow this exact structure:

### 1. YAML Frontmatter
```yaml
---
name: "Generic Component Name (not project-specific)"
description: "What this skill does (generic description)"
allowed-tools:
  - file_read
  - file_write
  - mcp_kubernetes_*
  - terminal
  - (other relevant tools)
---
```

### 2. Persona Section
```markdown
## Persona

You are a [specific role] specializing in [domain expertise].
```

### 3. Questions Section
```markdown
## Questions

Before acting, ask yourself:

1. [First reasoning question]
2. [Second reasoning question]
3. [Third reasoning question]
4. [Fourth reasoning question (if needed)]
5. [Fifth reasoning question (if needed)]
```

### 4. Principles Section
```markdown
## Principles

- [First principle]
- [Second principle]
- [Third principle]
- [Additional principles as needed]
```

### 5. Process Section
```markdown
## Process

1. **Read Specification:**
   - Read specification file: `specs/{spec-name}-spec.md`
   - Extract all required configuration values
   - Store in variables (never hardcode)

2. **Validate via MCP:**
   - Use MCP tools to verify current state
   - Check for conflicts or existing resources

3. **Implementation Steps:**
   - Step-by-step using extracted values
   - Reference variables, not hardcoded values

4. **Validation:**
   - Use MCP to verify deployment
   - Confirm all requirements met
```

### 6. MCP Code Execution Section
```markdown
## MCP Code Execution

### Before Implementation:
- Use `mcp_kubernetes_list_namespaces` to verify namespace
- Use `mcp_kubernetes_get_configmap` to check existing configs

### During Implementation:
- Use MCP tools to create resources
- Monitor via MCP status checks

### After Implementation:
- Use `mcp_kubernetes_get_deployment` to verify deployment
- Use `mcp_kubernetes_list_pods` to check pod health
- Use `mcp_kubernetes_get_service` to verify service

### Error Handling:
- If MCP returns error, log details
- Retry with exponential backoff
- Report failures clearly
```

---

## 6. Specification File Reading

### How to Read Specs:
1. **Locate specification file:** `specs/{component-name}-spec.md`
2. **Extract values systematically:**
   - Read the entire spec file first
   - Identify all configuration values needed
   - Extract using clear variable names
   - Document what each variable represents

### Common Spec Patterns:
- `spec.namespace` - Kubernetes namespace
- `spec.kafka.topics[]` - Array of Kafka topics
- `spec.api.endpoints[]` - API endpoints
- `spec.service.port` - Service port
- `spec.database.name` - Database name
- `spec.deployment.replicas` - Number of replicas
- `spec.metadata.project` - Project name (if needed)

### Example Extraction:
```markdown
From `specs/kafka-setup-spec.md`:
- namespace = spec.namespace (e.g., "production")
- topics = spec.kafka.topics (e.g., ["user-events", "payment-events"])
- retention = spec.kafka.retention (e.g., "7d")
- replication = spec.kafka.replication (e.g., 3)
```

---

## 7. Quality Checklist

Before finalizing each Skill, verify:

- [ ] **P+Q+P Framework:** Persona, Questions (3-5), and Principles sections present
- [ ] **MCP Integration:** MCP Code Execution section with specific tools and patterns
- [ ] **No Hardcoded Values:** All values read from specification files
- [ ] **Generic Names:** Component names are generic (not project-specific)
- [ ] **YAML Frontmatter:** Proper frontmatter with name, description, allowed-tools
- [ ] **Complete Structure:** All 6 sections present (Frontmatter, Persona, Questions, Principles, Process, MCP)
- [ ] **Cross-Agent Compatible:** No agent-specific syntax
- [ ] **Spec-Driven:** Process section explicitly reads from spec files
- [ ] **MCP Validation:** Validation steps use MCP tools, not assumptions
- [ ] **Error Handling:** Clear error handling patterns defined

---

## 8. Example Skill Template

```markdown
---
name: "Kafka Setup"
description: "Sets up Kafka infrastructure in Kubernetes using Helm, reading all configuration from specification files"
allowed-tools:
  - file_read
  - file_write
  - mcp_kubernetes_*
  - terminal
---

## Persona

You are a cloud-native infrastructure engineer specializing in Kafka, Kubernetes, and Helm. You understand distributed systems, event streaming architecture, and production-grade deployments.

## Questions

Before acting, ask yourself:

1. What configuration values do I need to extract from the Kafka specification file?
2. What is the current state of the Kubernetes cluster for Kafka resources?
3. Are there any existing Kafka topics or configurations that might conflict?
4. What validation steps are required to confirm Kafka is properly deployed and operational?
5. How can I verify this implementation matches all specification requirements?

## Principles

- Always read all configuration from `specs/kafka-setup-spec.md`, never hardcode values
- Validate all deployments via MCP Kubernetes server before proceeding
- Use Helm charts for Kafka deployment (Helm-first approach)
- Verify actual cluster state via MCP, never assume resources exist
- Follow Kafka best practices: proper topic partitioning, replication, and retention policies
- Ensure idempotency: check if resources exist before creating them

## Process

1. **Read Specification:**
   - Read `specs/kafka-setup-spec.md`
   - Extract namespace: `spec.namespace`
   - Extract topics: `spec.kafka.topics[]` (array of topic objects)
   - Extract retention policy: `spec.kafka.defaultRetention`
   - Extract replication factor: `spec.kafka.replicationFactor`
   - Extract storage class: `spec.kafka.storage.class`
   - Extract storage size: `spec.kafka.storage.size`

2. **Validate via MCP:**
   - Use `mcp_kubernetes_list_namespaces` to verify namespace exists
   - Use `mcp_kubernetes_list_pods` to check for existing Kafka pods
   - Verify cluster has sufficient resources

3. **Prepare Helm Values:**
   - Create `helm/kafka/values.yaml` using extracted values
   - Use variables: `{{ namespace }}`, `{{ topics }}`, `{{ retention }}`, etc.
   - Never hardcode project names or specific values

4. **Deploy Kafka:**
   - Install Kafka using Helm with extracted configuration
   - Use extracted namespace for deployment
   - Monitor deployment via MCP

5. **Create Topics:**
   - For each topic in `spec.kafka.topics[]`:
     - Extract topic name: `topic.name`
     - Extract partitions: `topic.partitions`
     - Extract replication: `topic.replication` (or use default)
     - Create topic using extracted values

6. **Validation:**
   - Use MCP to verify Kafka pods are running
   - Use MCP to verify topics are created
   - Confirm all requirements from spec are met

## MCP Code Execution

### Before Implementation:
- `mcp_kubernetes_list_namespaces`: Verify namespace exists
- `mcp_kubernetes_list_pods --namespace {extracted_namespace}`: Check for existing Kafka pods
- `mcp_kubernetes_get_storageclass`: Verify storage class exists

### During Implementation:
- `mcp_kubernetes_apply`: Apply Helm-generated manifests
- `mcp_kubernetes_list_pods --namespace {extracted_namespace} --label-selector app=kafka`: Monitor pod creation

### After Implementation:
- `mcp_kubernetes_get_deployment --namespace {extracted_namespace} --name kafka`: Verify deployment status
- `mcp_kubernetes_list_pods --namespace {extracted_namespace} --label-selector app=kafka`: Check pod health
- `mcp_kubernetes_get_service --namespace {extracted_namespace} --name kafka`: Verify service

### Error Handling:
- If MCP returns namespace not found: Create namespace first
- If MCP returns pod errors: Check logs via `mcp_kubernetes_get_pod_logs`
- If MCP returns deployment errors: Review Helm values and retry
- Always log MCP responses for debugging
```

---

## 9. Final Instructions

When creating Skills:

1. **Review all specs:** Read every file in `specs/` directory
2. **Create one Skill per spec:** Each specification file gets its own Skill
3. **Follow this prompt exactly:** Don't skip any requirements
4. **Verify reusability:** Ask yourself "Would this work for a different project?" If not, make it generic
5. **Test the structure:** Ensure all 6 sections are present and complete
6. **Validate MCP integration:** Ensure MCP tools are specified and used correctly

---

## 10. Common Mistakes to Avoid

### ❌ Don't:
- Hardcode any project-specific values
- Skip MCP validation steps
- Use project names in Skill names or descriptions
- Assume cluster state without MCP verification
- Create Skills without P+Q+P framework
- Use agent-specific syntax
- Hardcode ports, namespaces, topics, or URLs

### ✅ Do:
- Read all values from specification files
- Use MCP for all validation
- Use generic component names
- Verify state via MCP before and after
- Include complete P+Q+P framework
- Use standard markdown/YAML
- Extract everything from specs

---

*This prompt ensures Skills are created correctly, are reusable across projects, and follow Spec-Kit Plus best practices.*

