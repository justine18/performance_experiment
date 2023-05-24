using JuMP
using JSON
using DataFrames
using BenchmarkTools
using Gurobi
using SparseVariables

function read_tuple_list(filename)
    return [tuple(x...) for x in JSON.parsefile(filename)]
end

function read_fixed_data()
    N = open(JSON.parse, "supply_chain/data/data_N.json")
    L = open(JSON.parse, "supply_chain/data/data_L.json")
    M = open(JSON.parse, "supply_chain/data/data_M.json")
    JK = read_tuple_list("supply_chain/data/data_JK.json")
    KL = read_tuple_list("supply_chain/data/data_KL.json")
    LM = read_tuple_list("supply_chain/data/data_LM.json")
    return N, L, M, JK, KL, LM
end

function read_variable_data(n)
    I = ["i$i" for i in 1:n]
    IJ = read_tuple_list("supply_chain/data/data_IJ_$n.json")
    IK = read_tuple_list("supply_chain/data/data_IK_$n.json")
    d = read_tuple_list("supply_chain/data/data_D_$n.json")
    D = Dict()
    for x in d
        D[(x[1], x[2])] = x[3]
    end
    return I, IJ, IK, D
end

function deriveJK(IJ, IK, JK, KL)
    J =[]
    K = []
    for (j,k) in JK
        push!(J,j)
        push!(K,k)
    end
    for (k, _) in KL
        push!(K, k)
    end
    for (_, j) in IJ
        push!(J,j)
    end
    for (_, k) in IK
        push!(K, k)
    end
    return sort( unique(J), by=x->parse(Int, x[2:end])), sort(unique(K), by=x->parse(Int, x[2:end]))
end

function sparse_jump(I, J, K, L, M, IJ, JK, IK, KL, LM, D, solve)
    model = Model()

    @variable(model, x[i=I ,j=J, k=K] >= 0, container=IndexedVarArray)
    for (i, j) in IJ, (jj, k) in JK
        if jj == j
            for (ii, kk) in IK 
                if ii == i && kk == k
                    unsafe_insertvar!(x, i, j, k) # unsafe_insertvar! to skip checking valid index/duplicates
                end
            end
        end
    end
    @variable(model, y[i=I, k=K, l=L] >= 0, container=IndexedVarArray)
    for i in I, (k, l) in KL
        unsafe_insertvar!(y, i, k, l)
    end
    @variable(model, z[i=I, l=L, m=M] >= 0, container=IndexedVarArray)
    for i in I, (l, m) in LM
        unsafe_insertvar!(z, i, l, m)
    end

    for (i,k) in IK
        @constraint(model,
        sum(
            x[i, j, k]
            for (ii, j) in IJ if ii == i
            for (jj, kk) in JK if jj == j && kk == k
        ) >= sum(y[i, k, l] for (kk, l) in KL if kk == k)
        )
    end

    for i in I, l in L
        @constraint(model, 
        sum(
            y[i, k, l] for (k, ll) in KL if ll == l
        ) >= sum(z[i, l, m] for (ll, m) in LM if ll == l))
    end

    for i in I, m in M
    @constraint(model, 
    sum(
        z[i, l, m] for (l, mm) in LM if mm == m
    ) >= D[(i, m)])
    end
    # write_to_file(model, "sparse.lp")

    if solve == "True"
        set_optimizer(model, HiGHS.Optimizer)
        set_silent(model)
        optimize!(model)
    end
end

function intuitive_jump(I, L, M, IJ, JK, IK, KL, LM, D, solve)
    model = Model()

    x_list = [
        (i, j, k)
        for (i, j) in IJ
        for (jj, k) in JK if jj == j
        for (ii, kk) in IK if ii == i && kk == k
    ]

    y_list = [
        (i, k, l)
        for i in I
        for (k, l) in KL
    ]

    z_list = [(i, l, m) for i in I for (l, m) in LM]

    @variable(model, x[x_list] >= 0)
    @variable(model, y[y_list] >= 0)
    @variable(model, z[z_list] >= 0)

    @constraint(model, production[(i, k) in IK], sum(
        x[(i, j, k)]
        for (ii, j) in IJ if ii == i
        for (jj, kk) in JK if jj == j && kk == k
    ) >= sum(y[(i, k, l)] for (kk, l) in KL if kk == k)
    )

    @constraint(model, transport[i in I, l in L], sum(
        y[(i, k, l)] for (k, ll) in KL if ll == l
    ) >= sum(z[(i, l, m)] for (ll, m) in LM if ll == l))

    @constraint(model, demand[i in I, m in M], sum(
        z[(i, l, m)] for (l, mm) in LM if mm == m
    ) >= D[i, m])

    # write_to_file(model, "int.lp")

    if solve == "True"
        set_optimizer(model, Gurobi.Optimizer)
        set_silent(model)
        optimize!(model)
    end
end

function jump(I, L, M, IJ, JK, IK, KL, LM, D, solve)
    model = if solve == "True"
        direct_model(Gurobi.Optimizer())
    else
        Model()
    end

    set_string_names_on_creation(model, false)

    x_list = [
        (i, j, k)
        for (i, j) in IJ
        for (jj, k) in JK if jj == j
        for (ii, kk) in IK if ii == i && kk == k
    ]

    y_list = [
        (i, k, l)
        for i in I
        for (k, l) in KL
    ]

    z_list = [(i, l, m) for i in I for (l, m) in LM]

    @variable(model, x[x_list] >= 0)
    @variable(model, y[y_list] >= 0)
    @variable(model, z[z_list] >= 0)

    for (i, k) in IK
        @constraint(model,
            sum(
                x[(i, j, k)]
                for (ii, j) in IJ if ii == i
                for (jj, kk) in JK if jj == j && kk == k
            ) >= sum(y[(i, k, l)] for (kk, l) in KL if kk == k)
        )
    end

    for i in I, l in L
        @constraint(model,
            sum(y[(i, k, l)] for (k, ll) in KL if ll == l) >=
            sum(z[(i, l, m)] for (ll, m) in LM if ll == l))
    end

    for i in I, m in M
        @constraint(model, sum(z[(i, l, m)] for (l, mm) in LM if mm == m) >= D[i, m])
    end
    
    if solve == "True"
        set_silent(model)
        optimize!(model)
    end
end

# solve = false
# samples = 2
# evals = 1
# time_limit = 5

solve = ARGS[1]
samples = parse(Int64, ARGS[2])
evals = parse(Int64, ARGS[3])
time_limit = parse(Int64, ARGS[4])

N, L, M, JK, KL, LM = read_fixed_data()

t = DataFrame(I=Int[], Language=String[], MinTime=Float64[], MeanTime=Float64[], MedianTime=Float64[])
ts = DataFrame(I=Int[], Language=String[], MinTime=Float64[], MeanTime=Float64[], MedianTime=Float64[])
tt = DataFrame(I=Int[], Language=String[], MinTime=Float64[], MeanTime=Float64[], MedianTime=Float64[])

for n in N
    I, IJ, IK, D = read_variable_data(n)

    if maximum(t.MinTime; init=0) < time_limit
        r = @benchmark jump($I, $L, $M, $IJ, $JK, $IK, $KL, $LM, $D, $solve) samples = samples evals = evals
        push!(t, (n, "JuMP", minimum(r.times) / 1e9, mean(r.times) / 1e9, median(r.times) / 1e9))
        println("JuMP done $n in $(round(minimum(r.times) / 1e9, digits=2))s")
    end

    J, K = deriveJK(IJ, IK, JK, KL)
    if maximum(ts.MinTime; init=0) < time_limit
        r = @benchmark sparse_jump($I, $J, $K, $L, $M, $IJ, $JK, $IK, $KL, $LM, $D, $solve) samples = samples evals = evals
        push!(ts, (n, "Sparse JuMP", minimum(r.times) / 1e9, mean(r.times) / 1e9, median(r.times) / 1e9))
        println("Sparse JuMP done $n in $(round(minimum(r.times) / 1e9, digits=2))s")
    end

    if maximum(tt.MinTime; init=0) < time_limit
        rr = @benchmark intuitive_jump($I, $L, $M, $IJ, $JK, $IK, $KL, $LM, $D, $solve) samples = samples evals = evals
        push!(tt, (n, "Intuitive JuMP", minimum(rr.times) / 1e9, mean(rr.times) / 1e9, median(rr.times) / 1e9))
        println("Intuitive JuMP done $n in $(round(minimum(rr.times) / 1e9, digits=2))s")
    end
end

if solve == "True"
    file = "supply_chain/results/jump_results_solve.json"
    file2 = "supply_chain/results/intuitive_jump_results_solve.json"
else
    file = "supply_chain/results/jump_results_model.json"
    file2 = "supply_chain/results/intuitive_jump_results_model.json"
end

open(file, "w") do f
    JSON.print(f, t, 4)
end

open(file2, "w") do f
    JSON.print(f, tt, 4)
end

println("JuMP done")
